#!/usr/bin/env python3
"""
Generate portraits using InvokeAI REST API (v6.x)
This script creates workflow graphs and enqueues them for generation.

Requirements:
- InvokeAI running at http://localhost:9090
- requests library

Usage:
    python3 generate_with_api.py --single gilgamesh --prompt "Mesopotamian king..."
    python3 generate_with_api.py --all
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

# Configuration
BASE_DIR = Path(__file__).parent.parent.parent
PORTRAIT_DIR = BASE_DIR / "media" / "portraits"
INVOKEAI_URL = "http://localhost:9090"

# Character prompts
CHARACTER_PROMPTS = {
    "gilgamesh": {
        "positive": "Mesopotamian king of Uruk, Early Dynastic period 2700 BCE, two-thirds god one-third man, golden diadem crown with lapis lazuli inlays, white linen tunic with gold embroidery, kaunakes sheep-fleece skirt, wide leather belt with gold buckle, gold-decorated sandals, gold necklace bracelets signet ring, short well-kept hair, short curled beard, sword at belt, regal heroic pose, proud commanding expression, cinematic soft lighting from upper left, upper body portrait, historically accurate, high detail",
        "negative": "blurry, low resolution, modern clothing, fantasy elements, cartoon, anime, realistic photography, watermark, text, extra limbs, deformities, low detail"
    },
    "enkidu": {
        "positive": "Enkidu wild man from Epic of Gilgamesh, Early Dynastic period, strong muscular build, long matted hair covering shoulders and back, animal skin loincloth made from lion or deer, bare chest, long unkempt beard, intense focused expression, powerful primal pose standing on the steppe, natural lighting, upper body portrait, historically accurate Mesopotamian wild man, high detail",
        "negative": "blurry, modern elements, cartoon, anime, photography, watermark, text, clothing, clean groomed hair, civilization, human appearance"
    },
    "enkidu_civilized": {
        "positive": "Enkidu after civilization by Shamhat, Early Dynastic period, strong muscular build, simple headband, simple linen tunic, kaunakes or plain skirt, leather belt, sandals, one gold bracelet from Shamhat, long but cleaner hair, trimmed beard, noble expression, refined pose, soft temple lighting, upper body portrait, historically accurate, high detail",
        "negative": "blurry, wild appearance, animal skins, unkempt hair, cartoon, anime, photography, watermark, text"
    },
    "ishtar": {
        "positive": "Mesopotamian goddess Ishtar, goddess of love and war, horned headdress with multiple tiers and star motifs, lappets hanging down, red and gold ceremonial robes with intricate embroidery, lapis lazuli jewelry, carnelian inlays, gold sandals, heavy kohl eye makeup, red lips, long elaborately styled hair with braids, multiple gold necklaces bracelets armlets anklets earrings, ceremonial mace at side, beautiful yet terrifying expression, divine regal pose, ethereal lighting, upper body portrait, historically accurate Babylonian, high detail",
        "negative": "blurry, modern, cartoon, anime, photography, watermark, text, mortal appearance, humble, simple clothing, no makeup"
    },
    "shamhat": {
        "positive": "Temple priestess Shamhat of Ishtar, Early Dynastic period Uruk, gold headdress with lappets, white ceremonial robes with gold embroidery and patterns, long pleated linen dress, gold belt with precious stones, gold sandals, gold necklace with lapis lazuli, gold bracelets and earrings, small ceremonial bronze knife at belt, long elaborately styled black hair, subtle kohl eye makeup, elegant wise pose with hands clasped, kind noble expression, soft temple lighting, upper body portrait, historically accurate, high detail",
        "negative": "blurry, modern, cartoon, anime, photography, watermark, text, servant appearance, commoner clothing, messy hair"
    },
    "humbaba": {
        "positive": "Humbaba monster guardian of the Sacred Cedar Forest, sevenfold terrors, monstrous face with exaggerated features, large nose wide mouth, animal skins and furs draped over body, bone armor plates, massive stone club weapon, terrifying appearance, fierce intense expression with glowing eyes, menacing pose standing among cedar trees, dark forest lighting, full body portrait, Mesopotamian monster from epic, high detail",
        "negative": "blurry, human, beautiful, modern, cartoon, anime, photography, watermark, text, small, weak, friendly, civilized"
    },
    "utnapishtim": {
        "positive": "Utnapishtim the distant, survivor of the Great Flood, wise immortal elder, simple white headband or turban, long white robes with subtle patterns, staff in right hand, clay tablets at belt, long white gray hair and beard, wrinkled wise face, wise kind expression, contemplative pose, soft peaceful lighting, upper body portrait, historically accurate ancient Mesopotamian, high detail",
        "negative": "blurry, young, modern, cartoon, anime, photography, watermark, text, weak, foolish, short hair, colorful clothing"
    },
    "ur_shanabi": {
        "positive": "Ur-Shanabi the ferryman, practical working man, simple cloth turban head covering, plain linen loincloth or simple tunic, leather belt with pouch, oar or pole in hands, sandals or barefoot, practical short dark hair and beard, focused determined expression, working pose on wooden boat, soft water reflections, upper body portrait, historically accurate, high detail",
        "negative": "blurry, royal, wealthy, modern, cartoon, anime, photography, watermark, text, elaborate clothing, jewelry"
    },
    "scorpion_man": {
        "positive": "Scorpion Man guardian of Mount Mashu, half-man half-scorpion hybrid creature, human upper body with muscular torso and arms, human head with focused expression, scorpion lower body with segmented exoskeleton chitin armor, large pincers, curved segmented tail with stinger, brown and black chitin plates, stone elements, guarding pose at mountain gate, dramatic lighting, full body portrait, Mesopotamian guardian from Gilgamesh epic, high detail",
        "negative": "blurry, fully human, fully scorpion, modern, cartoon, anime, photography, watermark, text, friendly appearance, small size"
    },
    "ninsun": {
        "positive": "Ninsun mother of Gilgamesh, wise goddess, goddess headdress with divine symbols, white robes with gold embroidery, long flowing white skirt, gold belt, gold sandals, multiple gold jewelry pieces, long elaborately styled hair, heavy kohl eye makeup, wise divine expression, maternal pose, soft divine lighting, upper body portrait, historically accurate, high detail",
        "negative": "blurry, young, commoner, modern, cartoon, anime, photography, watermark, text, simple appearance, mortal"
    },
    "anu": {
        "positive": "Anu sky god father of Ishtar, supreme deity, horned headdress with multiple tiers representing heavens, white or blue robes with gold and lapis lazuli decorations, long flowing skirt, wide gold belt, gold sandals, extensive gold jewelry with lapis lazuli, scepter in hand, symbols of the sky, long white gray hair and beard elaborately curled, divine authority expression, regal pose on throne, ethereal heavenly lighting, upper body portrait, historically accurate, high detail",
        "negative": "blurry, mortal, modern, cartoon, anime, photography, watermark, text, earthly appearance, simple"
    },
    "bull_of_heaven": {
        "positive": "Bull of Heaven divine beast sent by Ishtar, massive divine bull with exaggerated features, powerful muscular body, large curved horns, red and black coloring as described in epic, terrifying appearance, fierce expression, smoke and fire effects around mouth and nostrils, charging pose, dramatic divine lighting, full body portrait, Mesopotamian divine creature, high detail",
        "negative": "blurry, normal bull, small, weak, modern, cartoon, anime, photography, watermark, text, friendly, mortal appearance"
    },
    "high_priest_anu": {
        "positive": "High Priest of Anu, traditional Mesopotamian priest, white headdress with lappets, white linen tunic and ceremonial robe, long skirt, lapis lazuli bead necklace worn as belt, white sandals, ceremonial bronze dagger at belt, clay tablet in hand, long well-kept black hair and beard, pious divine expression, prayer pose with hands raised, soft temple lighting, upper body portrait, historically accurate, high detail",
        "negative": "blurry, modern, cartoon, anime, photography, watermark, text, warrior, commoner, simple clothing, messy appearance"
    },
    "high_priestess_ishtar": {
        "positive": "High Priestess of Ishtar, ceremonial robes of love and war, star headdress with Ishtar symbols, red and gold robes with intricate embroidery, long skirt, gold belt, gold sandals, multiple gold jewelry pieces, ceremonial mace in hand, long elaborately styled hair, heavy makeup with kohl and red, regal powerful expression, divine pose, soft temple lighting with red accents, upper body portrait, historically accurate, high detail",
        "negative": "blurry, modern, cartoon, anime, photography, watermark, text, simple appearance, commoner, humble"
    },
    "temple_scribe": {
        "positive": "Mesopotamian temple scribe, scholar appearance, simple white headband, plain white linen tunic, plain skirt, clay tablets in leather satchel over shoulder, reed stylus at belt, sandals, practical short black hair and beard, focused scholarly expression, reading pose with stylus in hand, soft library lighting, upper body portrait, historically accurate, high detail",
        "negative": "blurry, modern, cartoon, anime, photography, watermark, text, warrior, noble, elaborate clothing"
    },
    "royal_guard": {
        "positive": "Royal Guard of Uruk, elite soldier, plumed bronze helmet with horsehair crest, bronze scale armor cuirass, leather skirt over armor, bronze greaves on legs, leather boots, sword at belt and spear in hand, short practical hair and beard, formidable guarding expression, alert pose, soft palace lighting, full body portrait, historically accurate Akkadian period, high detail",
        "negative": "blurry, commoner, modern, cartoon, anime, photography, watermark, text, simple clothing, no armor"
    },
    "uruk_noble": {
        "positive": "Uruk Noble wealthy citizen, turban or cylinder hat, fine linen tunic with gold embroidery at edges, long skirt, gold belt, gold sandals, gold jewelry necklace bracelets rings, staff or walking stick in hand, well-kept black hair and beard, refined noble expression, elegant pose, soft palace lighting, upper body portrait, historically accurate Early Dynastic, high detail",
        "negative": "blurry, poor, modern, cartoon, anime, photography, watermark, text, simple clothing, messy appearance"
    },
    "uruk_merchant": {
        "positive": "Uruk Merchant trader, colorful turban head covering, colorful tunic with patterns, plain skirt, balance scale hanging from belt, leather money pouch at waist, practical sandals, short practical hair and beard, shrewd trading expression, offering pose with hands extended, bustling market lighting, upper body portrait, historically accurate, high detail",
        "negative": "blurry, noble, modern, cartoon, anime, photography, watermark, text, simple clothing, wealthy appearance"
    },
    "potter": {
        "positive": "Mesopotamian potter craftsman, simple cloth head covering, plain linen tunic stained with clay, plain skirt, clay-covered leather apron, wooden tools at belt, barefoot or simple sandals, clay dust on hands and clothes, short practical hair, focused working expression, shaping clay pose with hands on pottery, workshop lighting, upper body portrait, historically accurate, high detail",
        "negative": "blurry, noble, modern, cartoon, anime, photography, watermark, text, clean appearance, no clay"
    },
    "weaver": {
        "positive": "Mesopotamian weaver textile worker, simple head covering shawl, plain dress with woven patterns, long skirt, shuttle at belt, fabric samples in hand, barefoot or simple sandals, practical covered hair, focused working expression, weaving pose with hands busy, soft home lighting, upper body portrait, historically accurate, high detail",
        "negative": "blurry, noble, modern, cartoon, anime, photography, watermark, text, elaborate clothing, idle pose"
    }
}

# All characters
CHARACTERS = list(CHARACTER_PROMPTS.keys())


def get_client():
    """Get HTTP client with base URL"""
    return requests.Session()


def check_api():
    """Check if InvokeAI API is running"""
    try:
        response = requests.get(f"{INVOKEAI_URL}/api/v1/auth/status", timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Cannot connect to InvokeAI API: {e}")
        return False


def get_models_dict(model_type="main"):
    """Get list of available models as dict"""
    try:
        response = requests.get(f"{INVOKEAI_URL}/api/v2/models/?model_type={model_type}")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return {m.get("key"): m for m in models if m.get("key")}
        return {}
    except Exception as e:
        print(f"⚠️  Warning: Could not fetch models: {e}")
        return {}


def get_models():
    """Get list of available main models"""
    return get_models_dict("main")


def get_model_info(model_key):
    """Get information about a specific model"""
    try:
        response = requests.get(f"{INVOKEAI_URL}/api/v2/models/i/{model_key}")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"⚠️  Warning: Could not fetch model info: {e}")
        return None


def create_text2img_graph(prompt, negative_prompt, model_key, width=512, height=512, steps=50, cfg_scale=10, seed=None):
    """Create a text-to-image generation graph for SDXL"""
    import random
    
    if seed is None:
        seed = random.randint(0, 2**32 - 1)
    
    # Get model info
    model_info = get_model_info(model_key)
    if not model_info:
        raise ValueError(f"Model {model_key} not found")
    
    is_sdxl = model_info.get("base") == "sdxl"
    
    # Build nodes
    nodes = {
        "model_loader": {
            "type": "sdxl_model_loader" if is_sdxl else "main_model_loader",
            "id": "model_loader",
            "model": {
                "key": model_info["key"],
                "hash": model_info["hash"],
                "name": model_info["name"],
                "base": model_info["base"],
                "type": model_info["type"]
            }
        },
        "positive_prompt": {
            "type": "sdxl_compel_prompt" if is_sdxl else "compel",
            "id": "positive_prompt",
            "prompt": prompt,
            **({"style": prompt} if is_sdxl else {})
        },
        "negative_prompt": {
            "type": "sdxl_compel_prompt" if is_sdxl else "compel",
            "id": "negative_prompt",
            "prompt": negative_prompt,
            **({"style": ""} if is_sdxl else {})
        },
        "noise": {
            "type": "noise",
            "id": "noise",
            "seed": seed,
            "width": width,
            "height": height,
            "use_cpu": False
        },
        "denoise": {
            "type": "denoise_latents",
            "id": "denoise",
            "steps": steps,
            "cfg_scale": cfg_scale,
            "scheduler": "euler",
            "denoising_start": 0,
            "denoising_end": 1
        },
        "latents_to_image": {
            "type": "l2i",
            "id": "latents_to_image"
        },
        "save_image": {
            "type": "save_image",
            "id": "save_image",
            "is_intermediate": False
        }
    }
    
    # Build edges
    edges = [
        {"source": {"node_id": "model_loader", "field": "unet"}, "destination": {"node_id": "denoise", "field": "unet"}},
        {"source": {"node_id": "model_loader", "field": "clip"}, "destination": {"node_id": "positive_prompt", "field": "clip"}},
        {"source": {"node_id": "model_loader", "field": "clip"}, "destination": {"node_id": "negative_prompt", "field": "clip"}},
    ]
    
    if is_sdxl:
        edges.extend([
            {"source": {"node_id": "model_loader", "field": "clip2"}, "destination": {"node_id": "positive_prompt", "field": "clip2"}},
            {"source": {"node_id": "model_loader", "field": "clip2"}, "destination": {"node_id": "negative_prompt", "field": "clip2"}},
        ])
        # Add VAE loader for SDXL - use a known SDXL VAE
        # Try to find an SDXL VAE model
        vae_models = get_models_dict("vae")
        vae_key = None
        for key, model in vae_models.items():
            if model.get("base") == "sdxl":
                vae_key = key
                break
        
        if vae_key:
            vae_info = get_model_info(vae_key)
            if vae_info:
                nodes["vae_loader"] = {
                    "type": "vae_loader",
                    "id": "vae_loader",
                    "vae_model": {
                        "key": vae_info["key"],
                        "hash": vae_info["hash"],
                        "name": vae_info["name"],
                        "base": vae_info["base"],
                        "type": vae_info["type"]
                    }
                }
                edges.append({"source": {"node_id": "vae_loader", "field": "vae"}, "destination": {"node_id": "latents_to_image", "field": "vae"}})
            else:
                edges.append({"source": {"node_id": "model_loader", "field": "vae"}, "destination": {"node_id": "latents_to_image", "field": "vae"}})
        else:
            edges.append({"source": {"node_id": "model_loader", "field": "vae"}, "destination": {"node_id": "latents_to_image", "field": "vae"}})
    else:
        edges.append({"source": {"node_id": "model_loader", "field": "vae"}, "destination": {"node_id": "latents_to_image", "field": "vae"}})
    
    edges.extend([
        {"source": {"node_id": "positive_prompt", "field": "conditioning"}, "destination": {"node_id": "denoise", "field": "positive_conditioning"}},
        {"source": {"node_id": "negative_prompt", "field": "conditioning"}, "destination": {"node_id": "denoise", "field": "negative_conditioning"}},
        {"source": {"node_id": "noise", "field": "noise"}, "destination": {"node_id": "denoise", "field": "noise"}},
        {"source": {"node_id": "denoise", "field": "latents"}, "destination": {"node_id": "latents_to_image", "field": "latents"}},
        {"source": {"node_id": "latents_to_image", "field": "image"}, "destination": {"node_id": "save_image", "field": "image"}},
    ])
    
    graph = {
        "id": f"text2img_{int(time.time())}",
        "nodes": nodes,
        "edges": edges
    }
    
    return graph


def enqueue_batch(graph, queue_id="default"):
    """Enqueue a batch for processing"""
    client = get_client()
    
    batch = {
        "batch": {
            "graph": graph,
            "runs": 1,
            "data": None
        }
    }
    
    print(f"   📤 Enqueuing batch...")
    
    try:
        response = client.post(
            f"{INVOKEAI_URL}/api/v1/queue/{queue_id}/enqueue_batch",
            json=batch,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to enqueue batch: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return None, None
        
        result = response.json()
        # The batch_id is nested in the response
        batch_id = result.get("batch", {}).get("batch_id")
        if not batch_id:
            print(f"❌ No batch_id in response: {json.dumps(result, indent=2)[:500]}")
            return None, None
        
        print(f"   📋 Batch ID: {batch_id}")
        return batch_id, result
    except Exception as e:
        print(f"   ❌ Exception during enqueue: {e}")
        return None, None


def wait_for_batch(batch_id, queue_id="default", timeout=300):
    """Wait for batch completion and return the most recent image"""
    client = get_client()
    start_time = time.time()
    
    while True:
        # Check timeout
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Batch {batch_id} timed out after {timeout} seconds")
        
        # Get batch status
        response = client.get(f"{INVOKEAI_URL}/api/v1/queue/{queue_id}/b/{batch_id}/status")
        if response.status_code != 200:
            print(f"⚠️  Warning: Could not get batch status: {response.status_code}")
            time.sleep(1)
            continue
        
        status_data = response.json()
        
        # Check for failures
        failed_count = status_data.get("failed", 0)
        if failed_count > 0:
            raise RuntimeError(f"Batch {batch_id} has {failed_count} failed item(s)")
        
        # Check completion
        completed = status_data.get("completed", 0)
        total = status_data.get("total", 0)
        
        if completed == total and total > 0:
            # Get most recent image
            images_response = client.get(f"{INVOKEAI_URL}/api/v1/images/?is_intermediate=false&limit=1")
            if images_response.status_code == 200:
                images_data = images_response.json()
                if images_data.get("items"):
                    return images_data["items"][0]["image_name"]
            return None
        
        # Wait before checking again
        time.sleep(2)


def get_image_url(image_name):
    """Get the URL for an image"""
    client = get_client()
    response = client.get(f"{INVOKEAI_URL}/api/v1/images/i/{image_name}/urls")
    if response.status_code == 200:
        data = response.json()
        return data.get("image_url", "")
    return ""


def get_image_data(image_name):
    """Get the image data (base64)"""
    client = get_client()
    response = client.get(f"{INVOKEAI_URL}/api/v1/images/i/{image_name}/full")
    if response.status_code == 200:
        return response.content
    return None


def save_image(image_data, output_path):
    """Save image data to file"""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(image_data)
        return True
    except Exception as e:
        print(f"❌ Error saving image: {e}")
        return False


def generate_single_portrait(character_id, model_key, width=512, height=512, steps=50, cfg_scale=10):
    """Generate a single portrait"""
    ensure_portrait_dir()
    
    if character_id not in CHARACTER_PROMPTS:
        print(f"⚠️  Warning: No prompt for {character_id}, skipping...")
        return False
    
    prompt_data = CHARACTER_PROMPTS[character_id]
    
    print(f"\n🎨 Generating {character_id}...")
    print(f"   Model: {model_key}")
    print(f"   Steps: {steps}, CFG: {cfg_scale}")
    print(f"   Prompt: {prompt_data['positive'][:80]}...")
    
    try:
        # Create graph
        graph = create_text2img_graph(
            prompt=prompt_data["positive"],
            negative_prompt=prompt_data["negative"],
            model_key=model_key,
            width=width,
            height=height,
            steps=steps,
            cfg_scale=cfg_scale
        )
        
        # Enqueue batch
        batch_id, result = enqueue_batch(graph)
        if batch_id is None:
            print(f"   ❌ Failed to enqueue batch")
            return False
        
        print(f"   📋 Batch ID: {batch_id}")
        
        # Wait for completion
        print(f"   ⏳ Waiting for generation...")
        image_name = wait_for_batch(batch_id)
        
        if image_name is None:
            print(f"   ❌ No image generated")
            return False
        
        print(f"   ✅ Image generated: {image_name}")
        
        # Get and save image
        image_data = get_image_data(image_name)
        if image_data is None:
            print(f"   ❌ Failed to download image")
            return False
        
        output_path = PORTRAIT_DIR / f"{character_id}.png"
        if save_image(image_data, output_path):
            print(f"   ✅ Saved: {output_path.name}")
            print(f"   📏 Size: {output_path.stat().st_size / 1024:.1f} KB")
            return True
        else:
            print(f"   ❌ Failed to save image")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def ensure_portrait_dir():
    """Create portrait directory if it doesn't exist"""
    PORTRAIT_DIR.mkdir(parents=True, exist_ok=True)
    return PORTRAIT_DIR


def main():
    parser = argparse.ArgumentParser(
        description="Generate Gilgamesh portraits using InvokeAI REST API"
    )
    parser.add_argument(
        "--model", type=str,
        default=None,
        help="Model key to use (default: first available SDXL model)"
    )
    parser.add_argument(
        "--steps", type=int, default=50,
        help="Number of diffusion steps (default: 50)"
    )
    parser.add_argument(
        "--cfg", type=int, default=10,
        help="CFG scale (default: 10)"
    )
    parser.add_argument(
        "--single", type=str, default=None,
        help="Generate only a single character"
    )
    parser.add_argument(
        "--width", type=int, default=512,
        help="Image width (default: 512)"
    )
    parser.add_argument(
        "--height", type=int, default=512,
        help="Image height (default: 512)"
    )
    
    args = parser.parse_args()
    
    print("\n🚀 Starting Gilgamesh Portrait Generation via API\n")
    
    # Check API
    if not check_api():
        print("\n❌ InvokeAI API not available at", INVOKEAI_URL)
        print("   Please start InvokeAI first")
        sys.exit(1)
    
    # Get available models
    models = get_models()
    if not models:
        print("\n❌ No models available")
        print("   Please install a model first")
        sys.exit(1)
    
    print(f"📋 Available models: {len(models)}")
    for key, model in models.items():
        print(f"   - {model.get('name', 'Unknown')} (key: {key}, base: {model.get('base', 'unknown')})")
    
    # Select model
    if args.model:
        if args.model not in models:
            print(f"\n❌ Model {args.model} not found")
            sys.exit(1)
        model_key = args.model
    else:
        # Find first SDXL model
        for key, model in models.items():
            if model.get("base") == "sdxl":
                model_key = key
                print(f"\n🔍 Using SDXL model: {model.get('name', 'Unknown')}")
                break
        else:
            # Use first available model
            model_key = list(models.keys())[0]
            print(f"\n🔍 Using model: {models[model_key].get('name', 'Unknown')}")
    
    ensure_portrait_dir()
    
    if args.single:
        # Generate only one character
        if args.single not in CHARACTER_PROMPTS:
            print(f"❌ Character '{args.single}' not found")
            sys.exit(1)
        
        success = generate_single_portrait(
            args.single, model_key, args.width, args.height, args.steps, args.cfg
        )
        
        if success:
            print(f"\n✅ {args.single} portrait generated successfully!")
            sys.exit(0)
        else:
            print(f"\n❌ Failed to generate {args.single}")
            sys.exit(1)
    else:
        # Generate all characters
        success_count = 0
        failed_count = 0
        total_count = len(CHARACTERS)
        
        for character_id in CHARACTERS:
            if generate_single_portrait(
                character_id, model_key, args.width, args.height, args.steps, args.cfg
            ):
                success_count += 1
            else:
                failed_count += 1
            
            # Small delay between requests
            time.sleep(1)
        
        print("\n" + "=" * 70)
        print(f"📊 Generation Summary")
        print("=" * 70)
        print(f"✅ Successful: {success_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"📋 Total: {total_count}")
        print(f"📈 Success Rate: {success_count/total_count*100:.1f}%")
        print("=" * 70)
        
        sys.exit(0 if success_count == total_count else 1)


if __name__ == "__main__":
    main()
