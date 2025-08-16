#!/usr/bin/env python3
"""
Emergency hotfix for missing _determine_alert_type method
Adds the missing method to the optimized emergency spike detector
"""

# Read the current detector file
with open('/home/ubuntu/crypto-trading-bot/emergency_spike_detector.py', 'r') as f:
    content = f.read()

# Add the missing method after the class definition
missing_method = '''    def _determine_alert_type(self, spike):
        """Determine alert type based on spike characteristics"""
        if spike.urgency_score >= 50:
            return 'CRITICAL'
        elif spike.urgency_score >= 35:
            return 'HIGH'
        elif spike.urgency_score >= 25:
            return 'MEDIUM'
        else:
            return 'LOW'

'''

# Find where to insert the method (after class definition)
class_line = "class ComprehensiveOpportunityScanner:"
if class_line in content:
    # Find the first method after class definition
    lines = content.split('\n')
    insert_index = -1
    for i, line in enumerate(lines):
        if class_line in line:
            # Find first method definition after this
            for j in range(i + 1, len(lines)):
                if lines[j].strip().startswith('def ') and not lines[j].strip().startswith('def __'):
                    insert_index = j
                    break
            break
    
    if insert_index > 0:
        # Insert the missing method
        lines.insert(insert_index, missing_method)
        fixed_content = '\n'.join(lines)
        
        # Write back the fixed content
        with open('/home/ubuntu/crypto-trading-bot/emergency_spike_detector.py', 'w') as f:
            f.write(fixed_content)
        
        print("✅ Missing method added successfully")
        print("🔄 Please restart the bot to apply the fix")
    else:
        print("❌ Could not find insertion point")
else:
    print("❌ Could not find class definition")
