#!/bin/bash
# InvokeAI Portrait Generation Script
# Uses the running InvokeAI instance at localhost:9090
# Or falls back to CLI if API not available

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PORTRAIT_DIR="$PROJECT_DIR/media/portraits"
INVOKEAI_URL="http://localhost:9090"

# Create portrait directory
mkdir -p "$PORTRAIT_DIR"

# Check if InvokeAI is running (web UI)
check_webui() {
    if curl -s "$INVOKEAI_URL" > /dev/null 2>&1; then
        echo "✅ InvokeAI Web UI found at $INVOKEAI_URL"
        return 0
    else
        echo "❌ InvokeAI Web UI not found at $INVOKEAI_URL"
        return 1
    fi
}

# Check if InvokeAI API is running
check_api() {
    # Try multiple endpoints
    for endpoint in "/api/v1/models" "/api/health" "/api/v1/health"; do
        if curl -s "$INVOKEAI_URL$endpoint" > /dev/null 2>&1; then
            echo "✅ InvokeAI API found at $INVOKEAI_URL$endpoint"
            return 0
        fi
    done
    echo "❌ InvokeAI API not found"
    return 1
}

# Check if InvokeAI CLI is available
check_cli() {
    if command -v invokeai > /dev/null 2>&1; then
        echo "✅ InvokeAI CLI found"
        return 0
    else
        echo "❌ InvokeAI CLI not found"
        return 1
    fi
}

# Generate using API v2 (preferred)
generate_api() {
    local model="${1:-sd-xl-base-1.0}"
    local steps="${2:-60}"
    local cfg="${3:-12}"
    local character="${4:-all}"
    
    if [ "$character" = "all" ]; then
        echo "Generating all portraits via API v2..."
        python3 "$SCRIPT_DIR/invokeai_api_v2.py" \
            --model "$model" \
            --steps "$steps" \
            --cfg "$cfg" \
            --convert
    else
        echo "Generating $character via API v2..."
        python3 "$SCRIPT_DIR/invokeai_api_v2.py" \
            --single "$character" \
            --model "$model" \
            --steps "$steps" \
            --cfg "$cfg" \
            --convert
    fi
}

# Generate using API v1 (fallback)
generate_api_v1() {
    local model="${1:-realistic_vision_v51}"
    local steps="${2:-50}"
    local cfg="${3:-10}"
    local character="${4:-all}"
    
    if [ "$character" = "all" ]; then
        echo "Generating all portraits via API v1..."
        python3 "$SCRIPT_DIR/invokeai_api_generate.py" \
            --model "$model" \
            --steps "$steps" \
            --cfg "$cfg" \
            --convert
    else
        echo "Generating $character via API v1..."
        python3 "$SCRIPT_DIR/invokeai_api_generate.py" \
            --single "$character" \
            --model "$model" \
            --steps "$steps" \
            --cfg "$cfg" \
            --convert
    fi
}

# Generate using CLI (fallback)
generate_cli() {
    local model="${1:-realistic_vision_v51.safetensors}"
    local steps="${2:-50}"
    local cfg="${3:-10}"
    local character="${4:-all}"
    
    if [ "$character" = "all" ]; then
        echo "Generating all portraits via CLI..."
        python3 "$SCRIPT_DIR/generate_portraits.py" \
            --model "$model" \
            --steps "$steps" \
            --cfg "$cfg" \
            --convert
    else
        echo "Generating $character via CLI..."
        python3 "$SCRIPT_DIR/generate_portraits.py" \
            --single "$character" \
            --model "$model" \
            --steps "$steps" \
            --cfg "$cfg" \
            --convert
    fi
}

# Main logic
case "${1:-all}" in
    gilgamesh|enkidu|ishtar|shamhat|humbaba|utnapishtim|ur_shanabi|scorpion_man|ninsun|anu|bull_of_heaven|high_priest_anu|high_priestess_ishtar|temple_scribe|royal_guard|uruk_noble|uruk_merchant|potter|weaver)
        character="$1"
        shift
        ;;
    *)
        character="all"
        ;;
esac

# Try API v2 first, then API v1, then CLI
if check_webui; then
    echo "Using API v2 (auto-discovery)..."
    generate_api "${2:-sd-xl-base-1.0}" "${3:-60}" "${4:-12}" "$character"
elif check_api; then
    echo "Using API v1..."
    generate_api_v1 "${2:-realistic_vision_v51}" "${3:-50}" "${4:-10}" "$character"
elif check_cli; then
    echo "Using CLI..."
    generate_cli "${2:-realistic_vision_v51.safetensors}" "${3:-50}" "${4:-10}" "$character"
else
    echo "❌ Neither InvokeAI API nor CLI is available"
    echo ""
    echo "To use InvokeAI API:"
    echo "  1. Start InvokeAI: invokeai --host 0.0.0.0 --port 9090"
    echo "  2. Then run this script again"
    echo ""
    echo "To use InvokeAI CLI:"
    echo "  1. Install InvokeAI: pip install invokeai"
    echo "  2. Download models: invokeai model download realistic_vision_v51.safetensors"
    echo "  3. Then run this script again"
    echo ""
    echo "For more info, see: tools/invokeai/README.md"
    exit 1
fi

echo ""
echo "✅ Portrait generation complete!"
echo "   Check: $PORTRAIT_DIR"
ls -lh "$PORTRAIT_DIR"/*.jpg "$PORTRAIT_DIR"/*.png 2>/dev/null | head -5
