# 🚀 AWS Storage Expansion Guide for Phase 3 Weeks 2-4

## 📊 Current Status
- **Current Volume**: 8GB (7GB usable)
- **Used**: 5.9GB
- **Available**: 831MB 
- **Phase 3 Needs**: 850MB additional

## ☁️ AWS EBS Volume Expansion Options

### Option A: Expand Current Volume (FREE - Recommended)
1. **In AWS Console**:
   - Go to EC2 → Volumes
   - Select your volume (attached to instance)
   - Actions → Modify Volume
   - Increase from 8GB to **15GB** or **20GB**
   
2. **On EC2 Instance**:
   ```bash
   # After AWS console expansion
   sudo growpart /dev/xvda 1
   sudo resize2fs /dev/xvda1
   ```

### Option B: Add Second EBS Volume (FREE)
1. **Create new 10GB volume**
2. **Attach to instance**
3. **Mount as /opt/crypto-ml**
4. **Move future Phase 3 features there**

## 💰 Cost Analysis
- **Current**: FREE (under free tier)
- **15GB Total**: Still FREE (free tier = 30GB)
- **20GB Total**: Still FREE (within limits)
- **Additional Volume**: FREE (separate 30GB allowance)

## 🎯 Recommended Action
**Expand to 20GB** - Gives us plenty of room for:
- ✅ Phase 3 Week 2: Advanced ML models
- ✅ Phase 3 Week 3: Real-time data feeds  
- ✅ Phase 3 Week 4: Advanced analytics
- ✅ TensorFlow full installation
- ✅ Future expansions
- ✅ Log growth
- ✅ Still within FREE tier

## 🔧 Alternative: Local Development
If AWS expansion not desired:
- Develop Weeks 2-4 locally
- Upload only final optimized versions
- Use AWS for production trading only

## ⚡ Immediate Actions Needed
1. **AWS Console**: Expand volume to 20GB
2. **SSH to instance**: Run resize commands
3. **Verify**: `df -h` shows new space
4. **Install**: Complete TensorFlow setup
5. **Proceed**: With Phase 3 Week 2 development

This keeps everything FREE and provides ample space for all Phase 3 features!
