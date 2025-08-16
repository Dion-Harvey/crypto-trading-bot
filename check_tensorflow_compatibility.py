#!/usr/bin/env python3
"""
TensorFlow Compatibility Checker
Checks Python version compatibility and suggests alternatives
"""

import sys
import subprocess
import platform

def check_python_version():
    """Check current Python version"""
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.machine()}")
    
    # TensorFlow compatibility check
    if version.major == 3:
        if version.minor >= 13:
            print("⚠️  WARNING: Python 3.13 may not be fully supported by TensorFlow yet")
            print("    TensorFlow officially supports Python 3.8-3.11")
            print("    Recommendation: Try tensorflow-cpu or wait for official support")
            return False
        elif version.minor >= 8:
            print("✅ Python version is compatible with TensorFlow")
            return True
        else:
            print("❌ Python version too old for TensorFlow 2.x")
            return False
    else:
        print("❌ Python 2.x not supported")
        return False

def try_alternative_installations():
    """Try different TensorFlow installation methods"""
    print("\n" + "="*50)
    print("TENSORFLOW INSTALLATION ALTERNATIVES")
    print("="*50)
    
    alternatives = [
        ("tensorflow-cpu", "CPU-only version (lighter, more compatible)"),
        ("tf-nightly", "Nightly build (may support newer Python versions)"),
        ("tensorflow==2.12.0", "Older stable version"),
        ("tensorflow==2.11.0", "Even older stable version"),
    ]
    
    for package, description in alternatives:
        print(f"\n📦 {package}")
        print(f"   {description}")
        print(f"   Command: python -m pip install {package}")

def check_current_packages():
    """Check what's currently installed"""
    print("\n" + "="*50)
    print("CURRENT AI/ML PACKAGES")
    print("="*50)
    
    try:
        import numpy as np
        print(f"✅ NumPy: {np.__version__}")
    except ImportError:
        print("❌ NumPy: Not installed")
    
    try:
        import pandas as pd
        print(f"✅ Pandas: {pd.__version__}")
    except ImportError:
        print("❌ Pandas: Not installed")
    
    try:
        import sklearn
        print(f"✅ Scikit-learn: {sklearn.__version__}")
    except ImportError:
        print("❌ Scikit-learn: Not installed")
    
    try:
        import tensorflow as tf
        print(f"✅ TensorFlow: {tf.__version__}")
        return True
    except ImportError:
        print("❌ TensorFlow: Not installed")
        return False

def suggest_alternative_approach():
    """Suggest alternative ML approaches if TensorFlow fails"""
    print("\n" + "="*50)
    print("ALTERNATIVE ML APPROACHES")
    print("="*50)
    
    print("If TensorFlow installation continues to fail, we can implement:")
    print("1. 📈 Enhanced Technical Analysis with Scikit-learn")
    print("   - Advanced regression models for price prediction")
    print("   - Ensemble methods (Random Forest, Gradient Boosting)")
    print("   - Feature engineering with existing indicators")
    
    print("\n2. 🧮 Statistical Models")
    print("   - ARIMA time series forecasting")
    print("   - Linear regression with polynomial features")
    print("   - Moving average convergence analysis")
    
    print("\n3. 🔄 Pattern Recognition")
    print("   - Candlestick pattern detection")
    print("   - Support/resistance level identification")
    print("   - Trend analysis algorithms")
    
    print("\n4. 📊 Signal Processing")
    print("   - Fourier analysis for cycle detection")
    print("   - Kalman filters for noise reduction")
    print("   - Wavelet transforms for multi-scale analysis")

if __name__ == "__main__":
    print("TensorFlow Compatibility Check")
    print("="*30)
    
    is_compatible = check_python_version()
    tensorflow_installed = check_current_packages()
    
    if not tensorflow_installed:
        try_alternative_installations()
        suggest_alternative_approach()
    else:
        print("\n✅ TensorFlow is already installed and working!")
    
    print("\n" + "="*50)
    print("RECOMMENDATION")
    print("="*50)
    
    if not is_compatible:
        print("🔄 Python 3.13 compatibility issue detected")
        print("   Try: python -m pip install tensorflow-cpu")
        print("   Or:  python -m pip install tf-nightly")
    else:
        print("✅ Environment should be compatible")
        print("   Try: python -m pip install tensorflow==2.13.0")
