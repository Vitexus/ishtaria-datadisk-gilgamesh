# Gilgamesh Datadisk Development Makefile
# Local development: validate, render voices, generate assets, stage, and run server

SHELL := /bin/bash
JOBS ?= $(shell nproc)
SERVER_DIR := ../ishtaria-server
PROTOCOL_DIR := ../ishtaria-protocol
DEV_DB ?= ishtaria_gilgamesh_dev
SEED ?= 43
BUILD := $(CURDIR)/build
PGM := $(BUILD)/world.pgm
STAGE := $(BUILD)/datadisks
DB_URL := postgresql:///$(DEV_DB)?host=/var/run/postgresql
WORLDGEN := $(abspath $(SERVER_DIR)/../ishtaria-worldgen/target/debug/ishtaria-worldgen)

.PHONY: check voices stage server start repin stop logs clean drop-db prompts models city world world-map sumer-map

check:
	python3 $(PROTOCOL_DIR)/tests/validate_datadisk.py .

# The real planet of the disk (media/world/): resample ETOPO 2022 once, then the ED reconstruction.
world:
	python3 tools/build_world_map.py

# The map of Sumer as it is in the game (maps/sumer.<lang>.png): land, sea, rivers, cities and roads read from this disk.
sumer-map:
	python3 tools/build_sumer_map.py

# The world heightmap strip worldgen renders from the disk's rasters (face size 256).
world-map: media/world/height.pgm media/world/water.pgm
	mkdir -p $(BUILD)
	cd ../ishtaria-worldgen && cargo build
	$(WORLDGEN) --seed $(SEED) --earth $(CURDIR)/media/world/height.pgm --water $(CURDIR)/media/world/water.pgm 256 > $(PGM)
	@echo "world heightmap: $$(stat -c%s $(PGM)) bytes"

voices:
	rm -rf $(BUILD)/voices
	python3 tools/render_voices.py --out $(BUILD)/voices --jobs $(JOBS)

stage: voices
	rm -rf $(STAGE)/gilgamesh
	mkdir -p $(STAGE)/gilgamesh
	cp -a datadisk.yaml places buildings trails rivers npcs dialogues quests lore knowledge.yaml achievements.yaml sky_flyers.yaml music media i18n $(STAGE)/gilgamesh/
	cp -a $(BUILD)/voices/media/. $(STAGE)/gilgamesh/media/
	@echo "staged: $$(find $(STAGE)/gilgamesh/media/voice -name '*.ogg' | wc -l) spoken lines"

$(BUILD)/server.toml:
	mkdir -p $(BUILD)
	sed -e 's|^listen = .*|listen = "127.0.0.1:7400"|' -e 's|^server_name = .*|server_name = "localhost"|' \
	    -e 's|^database_url = .*|database_url = "$(DB_URL)"|' $(SERVER_DIR)/etc/server.toml > $@

server: stage stop start

start: $(BUILD)/server.toml
	psql -lqt postgres | cut -d'|' -f1 | grep -qw $(DEV_DB) || createdb $(DEV_DB)
	cd $(SERVER_DIR) && cargo build --release --locked
	@first=""; \
	if [ "$$(psql -tA $(DEV_DB) -c "select to_regclass('worlds') is not null and exists(select 1 from worlds)" 2>/dev/null)" != "t" ]; then \
	  [ -s "$(PGM)" ] || $(MAKE) world-map; \
	  first="--import $(abspath $(PGM)) --seed $(SEED) --datadisk gilgamesh"; echo "creating the world in $(DEV_DB)"; fi; \
	cd $(SERVER_DIR) && ISHTARIA_DATADISK_DIR=$(STAGE) DATABASE_URL='$(DB_URL)' \
	  nohup ./target/release/ishtaria-server $(BUILD)/server.toml $$first > $(BUILD)/server.log 2>&1 & echo $$! > $(BUILD)/server.pid
	@for i in $$(seq 1 40); do curl -sf http://127.0.0.1:7400/health >/dev/null && { echo "server up: http://127.0.0.1:7400"; exit 0; }; sleep 0.5; done; \
	  echo "server did not come up, see $(BUILD)/server.log"; tail -20 $(BUILD)/server.log; exit 1

repin: stage stop
	psql -q $(DEV_DB) -c "UPDATE world_datadisks SET sha256 = NULL"
	$(MAKE) start

stop:
	@pkill -f '[i]shtaria-server $(BUILD)/server.toml' || true
	@rm -f $(BUILD)/server.pid
	@sleep 1

logs:
	tail -f $(BUILD)/server.log

clean: stop
	rm -rf $(BUILD)

drop-db: stop
	dropdb $(DEV_DB)

# Asset Generation Commands
prompts:
	@mkdir -p prompts
	python3 tools/generate_assets.py --portraits > prompts/portrait_prompts.json
	python3 tools/generate_assets.py --architecture > prompts/architecture_prompts.json
	python3 tools/generate_assets.py --cover > prompts/cover_prompt.json
	@echo "Generated prompts for AI image generation"

models:
	@mkdir -p media/models/architecture media/models/characters media/models/monsters
	@echo "Running Blender scripts..."
	@blender --background --python tools/blender/ziggurat_uruk.py 2>&1 | grep -E "(Creating|Exported|Done)" || echo "Blender not available"
	@echo "Blender scripts ready in tools/blender/"

clean-models:
	rm -rf media/models/architecture media/models/characters media/models/monsters
	@echo "Cleaned 3D models"

# InvokeAI Portrait Generation (uses REST API at localhost:9090)
# Requires InvokeAI running with REST API enabled
portraits-invokeai: 
	@mkdir -p media/portraits
	@echo "Generating all portraits with InvokeAI REST API..."
	cd tools/invokeai && python3 generate_with_api.py --steps 50 --cfg 10
	@echo "Portraits generated in media/portraits/"

portraits-gilgamesh: 
	@mkdir -p media/portraits
	@echo "Generating Gilgamesh portrait with InvokeAI REST API..."
	cd tools/invokeai && python3 generate_with_api.py --single gilgamesh --steps 50 --cfg 10

portraits-all:
	@mkdir -p media/portraits
	@echo "Generating all portraits with InvokeAI REST API (highest quality)..."
	cd tools/invokeai && python3 generate_with_api.py --steps 60 --cfg 12

portraits-fast:
	@mkdir -p media/portraits
	@echo "Generating all portraits with InvokeAI REST API (faster)..."
	cd tools/invokeai && python3 generate_with_api.py --steps 20 --cfg 7

# 3D Architecture Models (uses Blender in background mode)
models-architecture:
	@mkdir -p media/models/architecture
	@echo "Creating Mesopotamian architecture models..."
	@blender --background --python tools/blender/create_ziggurat.py -- ziggurat_simple media/models/architecture/ziggurat_simple.glb 2>&1 | grep -E "Creating|exported"
	@blender --background --python tools/blender/create_ziggurat.py -- ziggurat_etemenanki media/models/architecture/ziggurat_etemenanki.glb 2>&1 | grep -E "Creating|exported"
	@blender --background --python tools/blender/create_ziggurat.py -- temple media/models/architecture/temple.glb 2>&1 | grep -E "Creating|exported"
	@blender --background --python tools/blender/create_ziggurat.py -- city_gate media/models/architecture/city_gate.glb 2>&1 | grep -E "Creating|exported"
	@blender --background --python tools/blender/create_ziggurat.py -- complex media/models/architecture/ziggurat_complex.glb 2>&1 | grep -E "Creating|exported"
	@echo "Architecture models created in media/models/architecture/"

models-buildings:
	@mkdir -p media/models/architecture
	@echo "Creating additional Mesopotamian buildings..."
	@blender --background --python tools/blender/create_mesopotamian_building.py -- palace media/models/architecture/palace.glb 2>&1 | grep -E "Creating|exported"
	@blender --background --python tools/blender/create_mesopotamian_building.py -- residential media/models/architecture/residential.glb 2>&1 | grep -E "Creating|exported"
	@blender --background --python tools/blender/create_mesopotamian_building.py -- marketplace media/models/architecture/marketplace.glb 2>&1 | grep -E "Creating|exported"
	@blender --background --python tools/blender/create_mesopotamian_building.py -- grain_storage media/models/architecture/grain_storage.glb 2>&1 | grep -E "Creating|exported"
	@blender --background --python tools/blender/create_mesopotamian_building.py -- shrine media/models/architecture/shrine.glb 2>&1 | grep -E "Creating|exported"
	@echo "Building models created in media/models/architecture/"

models-architecture-all: models-architecture models-buildings

models: models-architecture-all

# Complete asset generation
assets: prompts models-architecture-all portraits-invokeai
	@echo "Asset generation complete!"
	@echo "Next steps:"
	@echo "  1. Test with: make stage server start"
	@echo "  2. Run: make stop clean to reset"
	@echo ""
	@echo "Individual commands:"
	@echo "  make portraits-invokeai    # Generate all portraits via REST API"
	@echo "  make portraits-fast        # Generate all portraits quickly"
	@echo "  make models-architecture    # Create ziggurats and gates"
	@echo "  make models-buildings      # Create palaces and houses"

# The streets, houses, markets, palaces and fields of Uruk: plan, then models (see research/CITY.md)
city:
	python3 tools/build_city.py
	python3 models-src/architecture/make_cone_mosaic.py
	python3 models-src/architecture/make_field_textures.py
	blender -b --factory-startup -P models-src/architecture/uruk_building_sites.py -- media/models/architecture
	python3 tools/build_buildings.py
	python3 tools/build_village.py
	python3 tools/build_uruk_wells.py
	blender -b --python models-src/architecture/uruk_city.py -- all media/models/architecture
	blender -b --python models-src/architecture/uruk_walls.py -- uruk_walls media/models/architecture/uruk_walls.glb
	blender -b --python models-src/architecture/uruk_walls.py -- uruk_walls_collision media/models/architecture/uruk_walls_collision.glb
