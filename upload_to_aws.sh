#!/bin/bash
# AWS Upload Script for Price Jump Detection Improvements
# Upload all enhanced files to AWS server

echo "🚀 Uploading Price Jump Detection Improvements to AWS..."

# Define the AWS server details
AWS_USER="ubuntu"
AWS_HOST="3.135.216.32"
AWS_PATH="~/crypto-trading-bot/"

# List of files to upload
FILES=(
    "bot.py"
    "enhanced_config.json" 
    "price_jump_detector.py"
    "multi_timeframe_ma.py"
    "PRICE_JUMP_IMPROVEMENTS.md"
    "PRICE_JUMP_ANALYSIS.md"
    "validate_improvements.py"
    "test_imports.py"
)

echo "📋 Files to upload:"
for file in "${FILES[@]}"; do
    echo "   - $file"
done

echo ""
echo "⚡ Uploading files..."

# Upload each file
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "📤 Uploading $file..."
        scp "$file" "$AWS_USER@$AWS_HOST:$AWS_PATH"
        if [ $? -eq 0 ]; then
            echo "   ✅ $file uploaded successfully"
        else
            echo "   ❌ $file upload failed"
        fi
    else
        echo "   ⚠️ $file not found locally"
    fi
done

echo ""
echo "🔍 Verifying uploads on AWS..."
ssh "$AWS_USER@$AWS_HOST" "cd $AWS_PATH && ls -la price_jump_detector.py multi_timeframe_ma.py"

echo ""
echo "🧪 Testing imports on AWS..."
ssh "$AWS_USER@$AWS_HOST" "cd $AWS_PATH && python3 test_imports.py"

echo ""
echo "✅ AWS upload complete!"
echo "🎯 Price jump detection improvements are now deployed on AWS"
