#!/usr/bin/env python3
"""
Asset Generation Script for Gilgamesh Datadisk

This script generates:
1. Detailed prompts for AI image generation (InvokeAI, Stable Diffusion, Midjourney)
2. Blender Python scripts for 3D models
3. Music and sound effect references
4. Asset organization

Usage:
    python3 generate_assets.py --portraits
    python3 generate_assets.py --models
    python3 generate_assets.py --music
    python3 generate_assets.py --all
"""

import argparse
import os
import json
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.parent
PORTRAIT_DIR = BASE_DIR / "media" / "portraits"
MODEL_DIR = BASE_DIR / "media" / "models"
MUSIC_DIR = BASE_DIR / "media" / "music"
COVER_DIR = BASE_DIR / "media" / "cover"
TEXTURE_DIR = BASE_DIR / "media" / "textures"
BLENDER_DIR = BASE_DIR / "tools" / "blender"

# Portrait Specifications
PORTRAIT_SIZE = (512, 512)
PORTRAIT_FORMAT = "PNG"
PORTRAIT_MAX_SIZE_MB = 1

# Character Data
CHARACTERS = {
    "gilgamesh": {
        "name": "Gilgamesh",
        "title": "King of Uruk, Two-Thirds God",
        "description": "Mighty king of Uruk, two-thirds god and one-third man. Heroic, strong, regal appearance.",
        "costume": {
            "head": "Golden diadem/crown with lapis lazuli inlays",
            "upper": "White linen tunic with gold embroidery",
            "lower": "Kaunakes (sheep-fleece skirt)",
            "belt": "Wide leather belt with gold buckle",
            "footwear": "Gold-decorated sandals",
            "jewelry": "Gold necklace, bracelets, signet ring",
            "hair": "Short to medium length, well-kept",
            "beard": "Short, curled",
            "weapons": "Sword at belt, dagger"
        },
        "pose": "Regal, confident, hero pose",
        "expression": "Proud, commanding",
        "style": "Historically accurate Mesopotamian royal portrait",
        "color_scheme": ["white", "gold", "lapis lazuli blue", "leather brown"],
        "period": "Early Dynastic (c. 2700 BCE)",
        "references": [
            "Standard of Ur royal figures",
            "Statues of Gudea (2120 BCE)",
            "Stele of Naram-Sin"
        ]
    },
    "enkidu": {
        "name": "Enkidu",
        "title": "Wild Man of the Steppes",
        "description": "Created from clay by the gods. Initially wild, then civilized by Shamhat. Strong, loyal companion to Gilgamesh.",
        "costume": {
            "wild": {
                "head": "Long, matted hair covering shoulders",
                "upper": "Bare chest",
                "lower": "Animal skin loincloth",
                "footwear": "Barefoot",
                "jewelry": "None",
                "hair": "Long, wild, matted",
                "beard": "Long, unkempt"
            },
            "civilized": {
                "head": "Simple headband",
                "upper": "Simple linen tunic",
                "lower": "Kaunakes or plain skirt",
                "belt": "Leather belt",
                "footwear": "Sandals",
                "jewelry": "Minimal (one bracelet)",
                "hair": "Long but cleaner",
                "beard": "Trimmed"
            }
        },
        "pose": "Powerful, primal (wild) or noble (civilized)",
        "expression": "Intense, focused",
        "style": "Wild and natural (wild) or refined (civilized)",
        "color_scheme": ["earth tones", "animal hide colors", "natural linen"],
        "period": "Early Dynastic",
        "references": ["Mesopotamian depictions of wild men", "Descriptions from epic text"]
    },
    "ishtar": {
        "name": "Ishtar",
        "title": "Goddess of Love and War",
        "description": "Beautiful and terrifying. Patron goddess of Uruk. Daughter of Anu.",
        "costume": {
            "head": "Horned headdress with star motifs and lappets",
            "upper": "Red and gold ceremonial robes",
            "lower": "Long, flowing skirt",
            "belt": "Gold belt with precious stone inlays",
            "footwear": "Gold sandals",
            "jewelry": "Multiple necklaces, bracelets, armlets, anklets, earrings",
            "weapons": "Mace or bow at side",
            "hair": "Long, elaborately styled",
            "makeup": "Heavy eye makeup (kohl), red lips"
        },
        "pose": "Regal, commanding, divine presence",
        "expression": "Beautiful yet terrifying",
        "style": "Divine, ethereal, godly",
        "color_scheme": ["red", "gold", "lapis lazuli", "carnelian"],
        "period": "All periods",
        "references": ["Ishtar Gate glazed bricks", "Votive statues", "Cylinder seals"]
    },
    "shamhat": {
        "name": "Shamhat",
        "title": "Temple Priestess",
        "description": "Priestess of Ishtar who civilizes Enkidu through love. Wise and compassionate.",
        "costume": {
            "head": "Gold headdress with lappets",
            "upper": "White ceremonial robes with gold embroidery",
            "lower": "Long, pleated dress",
            "belt": "Gold belt",
            "footwear": "Gold sandals",
            "jewelry": "Gold necklace, bracelets, earrings",
            "accessories": "Small ceremonial knife at belt",
            "hair": "Long, elaborately styled",
            "makeup": "Eye makeup, subtle"
        },
        "pose": "Elegant, wise, compassionate",
        "expression": "Kind, noble",
        "style": "Priestly, refined, sacred",
        "color_scheme": ["white", "gold"],
        "period": "Early Dynastic",
        "references": ["Statues of priestesses", "Cylinder seals with temple scenes"]
    },
    "humbaba": {
        "name": "Humbaba",
        "title": "Guardian of the Cedar Forest",
        "description": "Monster with sevenfold terrors. Guardian of the sacred Cedar Forest. Defeated by Gilgamesh and Enkidu.",
        "costume": {
            "head": "Monstrous face with exaggerated features",
            "upper": "Animal skins and furs draped",
            "lower": "Bone armor or scales",
            "footwear": "None or simple hide",
            "jewelry": "Stone and bone decorations",
            "weapons": "Massive club or axe",
            "special": "Sevenfold terrors (exaggerated facial features, terrifying appearance)"
        },
        "pose": "Menacing, monstrous, terrifying",
        "expression": "Fierce, terrifying",
        "style": "Monster, ogre-like, supernatural",
        "color_scheme": ["dark", "earthy", "terrifying"],
        "period": "Mythological",
        "references": ["Descriptions from epic text: 'his roar is a floodwater, his mouth is fire'", "Mesopotamian monster depictions"]
    },
    "utnapishtim": {
        "name": "Utnapishtim",
        "title": "Flood Survivor",
        "description": "Wise elder who survived the Great Flood. Granted eternal life by the gods. Lives across the Waters of Death.",
        "costume": {
            "head": "Simple headband or turban",
            "upper": "White robes",
            "lower": "Long skirt",
            "belt": "Simple leather belt",
            "footwear": "Sandals",
            "jewelry": "Minimal",
            "accessories": "Staff, clay tablets",
            "hair": "Long, white/gray",
            "beard": "Long, white/gray"
        },
        "pose": "Wise, ancient, contemplative",
        "expression": "Wise, kind",
        "style": "Elderly, wise, immortal",
        "color_scheme": ["white", "natural tones"],
        "period": "Later period",
        "references": ["Depictions of wise elders", "Descriptions from epic text"]
    },
    "ur_shanabi": {
        "name": "Ur-Shanabi",
        "title": "Ferryman",
        "description": "Ferries Gilgamesh across the Waters of Death to reach Utnapishtim.",
        "costume": {
            "head": "Simple cloth head covering",
            "upper": "Simple loincloth or tunic",
            "lower": "Plain skirt or loincloth",
            "footwear": "None or simple sandals",
            "jewelry": "None or minimal",
            "accessories": "Oar/pole, pouch at belt",
            "hair": "Practical, short",
            "beard": "Short, practical"
        },
        "pose": "Practical, working",
        "expression": "Focused, determined",
        "style": "Working class, practical",
        "color_scheme": ["natural", "practical"],
        "period": "Later period",
        "references": ["Depictions of boatmen", "Descriptions from epic text"]
    },
    "scorpion_man": {
        "name": "Scorpion Man",
        "title": "Guardian of Mount Mashu",
        "description": "Hybrid creature, half-man half-scorpion. Guards the gate to the tunnel through Mount Mashu.",
        "costume": {
            "upper": "Human torso with armor plates",
            "lower": "Scorpion body with chitin armor",
            "tail": "Segmented scorpion tail with stinger",
            "pincers": "Large, menacing",
            "color": "Human skin on upper body, chitin/armor on lower"
        },
        "pose": "Guarding, menacing",
        "expression": "Watchful, guarding",
        "style": "Hybrid creature, supernatural",
        "color_scheme": ["human tones", "brown/black chitin"],
        "period": "Mythological",
        "references": ["Descriptions from epic text", "Depictions of hybrid creatures"]
    },
    "ninsun": {
        "name": "Ninsun",
        "title": "Gilgamesh's Mother",
        "description": "Wise goddess, mother of Gilgamesh. Divinely wise.",
        "costume": {
            "head": "Goddess headdress",
            "upper": "White robes with gold embroidery",
            "lower": "Long, flowing skirt",
            "belt": "Gold belt",
            "footwear": "Gold sandals",
            "jewelry": "Multiple gold pieces",
            "hair": "Long, elaborately styled",
            "makeup": "Heavy eye makeup"
        },
        "pose": "Wise, divine, maternal",
        "expression": "Wise, divine",
        "style": "Divine, goddess-like",
        "color_scheme": ["white", "gold"],
        "period": "Early Dynastic",
        "references": ["Depictions of goddesses", "Descriptions from epic text"]
    },
    "anu": {
        "name": "Anu",
        "title": "Sky God",
        "description": "Father of Ishtar. Sky god, ruler of the heavens.",
        "costume": {
            "head": "Horned headdress with multiple tiers",
            "upper": "White or blue robes",
            "lower": "Long skirt",
            "belt": "Wide gold belt",
            "footwear": "Gold sandals",
            "jewelry": "Extensive gold with lapis lazuli",
            "accessories": "Scepter, symbols of sky",
            "hair": "Long, white/gray",
            "beard": "Long, white/gray, curled"
        },
        "pose": "Divine, regal, sky-like",
        "expression": "Wise, divine authority",
        "style": "Divine, sky god",
        "color_scheme": ["white", "blue", "gold"],
        "period": "All periods",
        "references": ["Standard depictions of sky gods", "Descriptions from religious texts"]
    },
    "bull_of_heaven": {
        "name": "Bull of Heaven",
        "title": "Divine Bull",
        "description": "Divine beast sent by Ishtar to punish Gilgamesh and Enkidu.",
        "costume": {
            "body": "Divine bull with exaggerated features",
            "color": "Red and black (as described in text)",
            "size": "Massive, larger than normal bull",
            "special": "Smoke, fire (optional effects)"
        },
        "pose": "Powerful, charging",
        "expression": "Fierce, divine",
        "style": "Divine animal, supernatural",
        "color_scheme": ["red", "black"],
        "period": "Mythological",
        "references": ["Descriptions from epic text (Tablet VI)", "Depictions of divine animals"]
    }
}

# Historical Figures
HISTORICAL_FIGURES = {
    "high_priest_anu": {
        "name": "High Priest of Anu",
        "title": "Traditional Priest",
        "description": "Priest serving the sky god Anu.",
        "costume": {
            "head": "White headdress with lappets",
            "upper": "White linen tunic and robe",
            "lower": "Long skirt",
            "belt": "Lapis lazuli bead necklace as belt",
            "footwear": "White sandals",
            "jewelry": "Ceremonial dagger, clay tablet at belt",
            "hair": "Long, well-kept",
            "beard": "Long, well-kept"
        },
        "pose": "Pious, divine",
        "style": "Pure and divine appearance",
        "color_scheme": ["white", "lapis lazuli blue"],
        "references": ["Priest statues", "Religious artifacts"]
    },
    "high_priestess_ishtar": {
        "name": "High Priestess of Ishtar",
        "title": "Priestess of Love and War",
        "description": "High priestess serving goddess Ishtar.",
        "costume": {
            "head": "Star headdress",
            "upper": "Red and gold robes",
            "lower": "Long skirt",
            "belt": "Gold belt",
            "footwear": "Gold sandals",
            "jewelry": "Multiple gold pieces, ceremonial mace",
            "hair": "Long, elaborately styled",
            "makeup": "Heavy"
        },
        "pose": "Regal, powerful",
        "style": "Regal and powerful",
        "color_scheme": ["red", "gold"],
        "references": ["Priestess statues", "Temple artifacts"]
    },
    "temple_scribe": {
        "name": "Temple Scribe",
        "title": "Scholar",
        "description": "Scholar who writes and reads cuneiform tablets.",
        "costume": {
            "head": "Simple headband",
            "upper": "White tunic",
            "lower": "Plain skirt",
            "accessories": "Clay tablets in satchel, reed stylus at belt",
            "footwear": "Sandals",
            "hair": "Practical cut",
            "beard": "Short"
        },
        "pose": "Scholarly, focused",
        "style": "Practical scholar appearance",
        "color_scheme": ["white", "natural"],
        "references": ["Scribe statues", "Cylinder seals with writing scenes"]
    },
    "royal_guard": {
        "name": "Royal Guard",
        "title": "Elite Soldier",
        "description": "Elite soldier protecting the king and palace.",
        "costume": {
            "head": "Plumed helmet",
            "upper": "Bronze scale armor",
            "lower": "Leather skirt over armor",
            "legs": "Bronze greaves",
            "footwear": "Leather boots",
            "weapons": "Sword and spear",
            "hair": "Short, practical",
            "beard": "Short, practical"
        },
        "pose": "Formidable, guarding",
        "style": "Formidable protector",
        "color_scheme": ["bronze", "leather brown"],
        "references": ["Soldier depictions", "Military artifacts"]
    },
    "uruk_noble": {
        "name": "Uruk Noble",
        "title": "Wealthy Citizen",
        "description": "Wealthy and refined citizen of Uruk.",
        "costume": {
            "head": "Turban or cylinder hat",
            "upper": "Fine linen tunic with embroidery",
            "lower": "Long skirt",
            "belt": "Gold belt",
            "footwear": "Gold sandals",
            "accessories": "Staff or walking stick",
            "jewelry": "Gold necklace, bracelets, rings",
            "hair": "Well-kept",
            "beard": "Well-kept, curled"
        },
        "pose": "Refined, noble",
        "style": "Wealthy and refined",
        "color_scheme": ["fine fabrics", "gold"],
        "references": ["Noble depictions", "Elite artifacts"]
    },
    "uruk_merchant": {
        "name": "Uruk Merchant",
        "title": "Trader",
        "description": "Practical but colorful trader.",
        "costume": {
            "head": "Turban",
            "upper": "Colorful tunic",
            "lower": "Skirt",
            "accessories": "Balance scale, money pouch",
            "footwear": "Practical sandals",
            "hair": "Practical",
            "beard": "Practical"
        },
        "pose": "Trading, practical",
        "style": "Practical but colorful",
        "color_scheme": ["various colors"],
        "references": ["Merchant depictions", "Trade artifacts"]
    },
    "potter": {
        "name": "Potter",
        "title": "Craftsman",
        "description": "Working craftsman creating pottery.",
        "costume": {
            "head": "Simple cloth covering",
            "upper": "Simple tunic",
            "lower": "Plain skirt",
            "accessories": "Clay-covered apron, wooden tools at belt",
            "footwear": "Barefoot or sandals",
            "hair": "Practical, possibly dusty"
        },
        "pose": "Working, focused",
        "style": "Working craftsman",
        "color_scheme": ["natural", "clay-stained"],
        "references": ["Craftsman depictions", "Pottery artifacts"]
    },
    "weaver": {
        "name": "Weaver",
        "title": "Textile Worker",
        "description": "Textile worker creating fabrics.",
        "costume": {
            "head": "Head covering",
            "upper": "Simple dress",
            "lower": "Long skirt",
            "accessories": "Shuttle at belt, fabric samples",
            "footwear": "Barefoot or sandals",
            "hair": "Practical, covered"
        },
        "pose": "Working, focused",
        "style": "Practical working woman",
        "color_scheme": ["natural fabrics"],
        "references": ["Weaver depictions", "Textile artifacts"]
    }
}

# Architecture Data
ARCHITECTURE = {
    "ziggurat_uruk": {
        "name": "Ziggurat of Uruk",
        "description": "Main ziggurat of Uruk, dedicated to the city's patron deities.",
        "dimensions": {
            "base_size": (60, 50),
            "height": 22,
            "tiers": 3
        },
        "materials": {
            "core": "mud brick",
            "exterior": "mud brick with white plaster finish",
            "decorations": "recessed panels, buttresses"
        },
        "features": [
            "Central staircase",
            "Temple at summit",
            "Small windows/slits for ventilation",
            "Decorative friezes near entrance"
        ],
        "historical_reference": "Based on Ziggurat of Ur (2100 BCE): 64m x 46m base, ~21m height, 3 tiered platforms"
    },
    "ziggurat_anu": {
        "name": "Ziggurat of Anu",
        "description": "Ziggurat dedicated to the sky god Anu.",
        "dimensions": {
            "base_size": (45, 45),
            "height": 20,
            "tiers": 3
        },
        "materials": {
            "core": "mud brick",
            "exterior": "darker mud brick",
            "decorations": "lapis lazuli inlays, white plaster accents"
        },
        "features": [
            "Single central staircase",
            "Smaller temple at summit",
            "Sky/star motifs in decoration"
        ],
        "historical_reference": "Similar to Ziggurat of Ur but with darker bricks and sky motifs"
    },
    "ziggurat_ishtar": {
        "name": "Ziggurat of Ishtar",
        "description": "Ziggurat dedicated to the goddess Ishtar.",
        "dimensions": {
            "base_size": (50, 50),
            "height": 22,
            "tiers": 3
        },
        "materials": {
            "core": "mud brick",
            "exterior": "red and pink plaster",
            "decorations": "carnelian inlays, gold accents"
        },
        "features": [
            "Multiple staircases",
            "Lion and star motifs",
            "Larger temple complex at top"
        ],
        "historical_reference": "Red plaster exterior with gold accents, dedicated to love and war goddess"
    },
    "white_temple": {
        "name": "White Temple",
        "description": "Whitewashed temple on a platform.",
        "dimensions": {
            "base_size": (30, 20),
            "height": 15,
            "tiers": 1
        },
        "materials": {
            "core": "mud brick",
            "exterior": "whitewashed plaster",
            "decorations": "clean geometric lines"
        },
        "features": [
            "Rectangular shape",
            "Niche decorations",
            "Flat roof with parapet"
        ],
        "historical_reference": "Based on White Temple of Uruk (3400-3000 BCE)"
    }
}

# Music Tracks
MUSIC_TRACKS = {
    "temple": {
        "name": "Temple Music",
        "description": "Sacred, mystical music for temples",
        "style": "Atmospheric, slow, sacred",
        "instruments": ["lyre", "harp", "flute", "drums"],
        "references": ["Mesopotamian temple music reconstructions", "Ancient Near Eastern music"]
    },
    "ishtar_shrine": {
        "name": "Ishtar's Temple Music",
        "description": "Music for the temple of Ishtar, goddess of love and war",
        "style": "Passionate, rhythmic",
        "instruments": ["lyre", "harp", "tambourine", "drums"],
        "references": ["Music associated with love and war goddesses"]
    },
    "cedar_forest": {
        "name": "Cedar Forest",
        "description": "Mysterious, dark music for the sacred Cedar Forest",
        "style": "Dark, mysterious, foreboding",
        "instruments": ["flute", "drums", "natural sounds"],
        "references": ["Forest ambience, ancient mystical music"]
    },
    "mountain_echo": {
        "name": "Mountain Echo",
        "description": "Echoing music for Mount Mashu and the Tunnel of the Sun",
        "style": "Echoing, cavernous, mysterious",
        "instruments": ["flute", "percussion", "echo effects"],
        "references": ["Mountain ambience, tunnel echoes"]
    },
    "waters_of_death": {
        "name": "Waters of Death",
        "description": "Ominous music for the deadly waters",
        "style": "Dark, ominous, water sounds",
        "instruments": ["deep drums", "water sounds", "low strings"],
        "references": ["Death associations, water mythology"]
    },
    "utnapishtim": {
        "name": "Utnapishtim's Dwelling",
        "description": "Peaceful music for the flood survivor's home",
        "style": "Peaceful, wise, serene",
        "instruments": ["lyre", "harp", "soft flute"],
        "references": ["Wisdom, immortality, peace"]
    }
}


def generate_portrait_prompts():
    """Generate detailed prompts for character portraits"""
    prompts = {}
    
    all_characters = {**CHARACTERS, **HISTORICAL_FIGURES}
    
    for char_id, char_data in all_characters.items():
        # Basic prompt
        prompt = f"""Mesopotamian {char_data['title'].lower()} from the Epic of Gilgamesh era, """
        
        # Description
        prompt += f"{char_data['description']}, "
        
        # Costume details
        if 'wild' in char_data.get('costume', {}):
            # For Enkidu, handle both versions
            prompt += f"shown in {char_data['costume']['wild']} (wild version), "
        elif 'costume' in char_data:
            costume = char_data['costume']
            if isinstance(costume, dict) and 'upper' in costume:
                prompt += "wearing "
                for part, detail in costume.items():
                    if part in ['special', 'color']:
                        continue
                    prompt += f"{detail}, "
        
        # Pose and expression
        prompt += f"{char_data['pose']}, {char_data['expression']}, "
        
        # Style
        prompt += f"{char_data['style']}, "
        
        # Color scheme
        colors = char_data.get('color_scheme', [])
        if colors:
            prompt += f"color scheme: {', '.join(colors)}, "
        
        # Period
        if 'period' in char_data:
            prompt += f"{char_data['period']}, "
        
        # References
        if 'references' in char_data:
            prompt += f"based on {char_data['references'][0]}, "
        
        # Technical details
        prompt += """upper body portrait, 512x512 pixels, transparent background, """
        prompt += "historically accurate, detailed costume, clean lines, "
        prompt += "soft lighting from upper left, cinematic, professional illustration, "
        prompt += "character focused, no modern elements, authentic Mesopotamian art style"
        
        # Negative prompt
        negative_prompt = "blurry, low resolution, modern clothing, fantasy elements, cartoon, anime, realistic photography, watermark, text"
        
        prompts[char_id] = {
            "positive": prompt,
            "negative": negative_prompt,
            "size": PORTRAIT_SIZE,
            "format": PORTRAIT_FORMAT,
            "max_size_mb": PORTRAIT_MAX_SIZE_MB,
            "style": "Portrait",
            "character_name": char_data['name'],
            "character_title": char_data['title']
        }
    
    return prompts


def generate_architecture_prompts():
    """Generate prompts for architecture concept art"""
    prompts = {}
    
    for arch_id, arch_data in ARCHITECTURE.items():
        prompt = f"""Ancient Mesopotamian {arch_data['name']}, """
        prompt += f"{arch_data['description']}, "
        
        # Dimensions
        size = arch_data['dimensions']['base_size']
        height = arch_data['dimensions']['height']
        prompt += f"base size approximately {size[0]}m x {size[1]}m, height approximately {height}m, "
        
        # Materials
        materials = arch_data['materials']
        prompt += f"constructed from {materials['core']}, finished with {materials['exterior']}, "
        if 'decorations' in materials:
            prompt += f"decorated with {materials['decorations']}, "
        
        # Features
        features = arch_data['features']
        prompt += f"featuring {', '.join(features)}, "
        
        # Historical accuracy
        prompt += f"{arch_data['historical_reference']}, "
        
        # Technical details
        prompt += "desert setting, golden hour lighting, highly detailed, "
        prompt += "architectural concept art, cinematic, professional, "
        prompt += "show multiple angles, include scale reference, "
        prompt += "accurate proportions, historical textures, weathering"
        
        negative_prompt = "modern architecture, anachronistic elements, fantasy structures, cartoon, low resolution, blurry, watermark, text"
        
        prompts[arch_id] = {
            "positive": prompt,
            "negative": negative_prompt,
            "size": (1024, 768),
            "format": "PNG",
            "style": "Concept Art",
            "name": arch_data['name']
        }
    
    return prompts


def generate_cover_prompt():
    """Generate prompt for datadisk cover image"""
    prompt = """Epic of Gilgamesh cover art, Gilgamesh and Enkidu in foreground, """
    prompt += "Ziggurat of Uruk in background, Cedar Forest elements, "
    prompt += "Gilgamesh wearing golden crown and white robes, "
    prompt += "Enkidu in kaunakes skirt and simple tunic, "
    prompt += "both heroes in heroic poses, "
    prompt += "Uruk ziggurats towering in background, "
    prompt += "golden hour lighting with dramatic shadows, "
    prompt += "clear blue sky with subtle clouds, "
    prompt += "title text 'Gilgamesh' at top, "
    prompt += "Mesopotamian art style, historically accurate, "
    prompt += "cinematic composition, wide shot, "
    prompt += "1024x768 pixels, highly detailed, professional fantasy art, "
    prompt += "epic atmosphere, authentic costumes and architecture"
    
    negative_prompt = "modern elements, anachronisms, fantasy creatures not in epic, cartoon, anime, low resolution, blurry, watermark, text (except title)"
    
    return {
        "cover": {
            "positive": prompt,
            "negative": negative_prompt,
            "size": (1024, 768),
            "format": "PNG",
            "style": "Cover Art"
        }
    }


def generate_music_references():
    """Generate music track references"""
    references = {}
    
    for track_id, track_data in MUSIC_TRACKS.items():
        references[track_id] = {
            "name": track_data['name'],
            "description": track_data['description'],
            "style": track_data['style'],
            "instruments": track_data['instruments'],
            "references": track_data['references'],
            "filename": f"{track_id}.ogg",
            "path": str(MUSIC_DIR / f"{track_id}.ogg"),
            "duration": "3-5 minutes (looping)",
            "format": "OGG Vorbis",
            "max_size_mb": 8,
            "sources": [
                "Free Music Archive (freemusicarchive.org)",
                "Incompetech (incompetech.com) - Kevin MacLeod",
                "Tabletop Audio (tabletopaudio.com) - 10-minute loops",
                "Search terms: Mesopotamian, ancient, middle eastern, ambient"
            ]
        }
    
    return references


def generate_blender_script_template(character_id, character_data):
    """Generate a Blender Python script template for a character"""
    script = f"""#!/usr/bin/env blender --background --python
"""
Character Model Script: {character_data['name']}
{character_data['title']}
Based on historical references from the Epic of Gilgamesh era

Scale: 1 Blender unit = 1 meter
Output: media/models/characters/{character_id}.glb

Historical Reference:
{character_data.get('period', 'Early Dynastic')}
{', '.join(character_data.get('references', []))}

Costume:
"""
    
    if 'costume' in character_data:
        costume = character_data['costume']
        if isinstance(costume, dict) and 'upper' in costume:
            for part, detail in costume.items():
                if part not in ['special', 'color']:
                    script += f"- {part.capitalize()}: {detail}\n"
    
    script += """
---

import bpy
import bmesh
import math
import os

OUTPUT_DIR = "//media/models/characters"
MODEL_NAME = "