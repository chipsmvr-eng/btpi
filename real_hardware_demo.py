#!/usr/bin/env python3
"""
REAL ChipWhisperer Demo - Captures actual hardware data
"""

import chipwhisperer as cw
import numpy as np
import matplotlib.pyplot as plt
import time
import random

class RealChipWhispererDemo:
    def __init__(self):
        self.scope = None
        self.target = None
        self.connected = False
        self.traces = []
        
    def connect(self):
        """Connect to real ChipWhisperer hardware"""
        try:
            print("🔌 Connecting to ChipWhisperer hardware...")
            self.scope = cw.scope()
            self.target = cw.target(self.scope, cw.targets.SimpleSerial)
            self.scope.default_setup()
            self.connected = True
            print("✅ Connected to real ChipWhisperer hardware!")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def test_target_communication(self):
        """Test that target is responding"""
        print("🧪 Testing target communication...")
        try:
            self.target.flush()
            
            # Test 'p' command
            self.target.simpleserial_write('p', bytearray([0xAA] * 16))
            time.sleep(0.2)
            response = self.target.read()
            print(f"   Target response: {len(response)} bytes")
            if response:
                print(f"   Response data: {response[:50]}...")
                return True
            else:
                print("   ⚠ No response from target")
                return False
        except Exception as e:
            print(f"   ❌ Communication test failed: {e}")
            return False
    
    def capture_real_trace(self, input_data):
        """Capture a single real power trace"""
        try:
            # Arm the scope
            self.scope.arm()
            
            # Send command to target
            self.target.simpleserial_write('p', bytearray(input_data))
            
            # Capture the trace
            self.scope.capture()
            
            # Get the trace data
            trace = self.scope.get_last_trace()
            
            return trace
        except Exception as e:
            print(f"   ❌ Trace capture failed: {e}")
            return None
    
    def capture_multiple_traces(self, num_traces=5):
        """Capture multiple real power traces with different inputs"""
        print(f"🔬 Capturing {num_traces} REAL power traces...")
        
        self.traces = []
        
        for i in range(num_traces):
            print(f"  📊 Trace {i+1}/{num_traces}...")
            
            # Use different input data for each trace
            input_data = [i % 256] * 16
            
            # Capture real trace
            trace = self.capture_real_trace(input_data)
            
            if trace is not None:
                self.traces.append(trace)
                print(f"    ✅ Captured {len(trace)} samples")
                
                # Show some trace statistics
                print(f"    📈 Range: {np.min(trace):.3f} to {np.max(trace):.3f}")
                print(f"    📊 Mean: {np.mean(trace):.3f}, Std: {np.std(trace):.3f}")
            else:
                print(f"    ❌ Failed to capture trace {i+1}")
        
        print(f"✅ Captured {len(self.traces)} real traces")
        return len(self.traces) > 0
    
    def analyze_traces(self):
        """Analyze the real captured traces"""
        if not self.traces:
            print("❌ No traces to analyze!")
            return False
        
        print("🧮 Analyzing REAL power traces...")
        
        # Convert to numpy array
        trace_array = np.array(self.traces)
        
        # Calculate statistics
        mean_trace = np.mean(trace_array, axis=0)
        std_trace = np.std(trace_array, axis=0)
        max_power = np.max(mean_trace)
        min_power = np.min(mean_trace)
        
        # Find interesting points (high variance)
        variance = np.var(trace_array, axis=0)
        mean_variance = np.mean(variance)
        interesting_points = np.where(variance > mean_variance * 1.5)[0]
        
        # Calculate correlation between traces
        if len(self.traces) > 1:
            correlations = []
            for i in range(len(self.traces)):
                for j in range(i+1, len(self.traces)):
                    corr = np.corrcoef(self.traces[i], self.traces[j])[0,1]
                    correlations.append(corr)
            avg_correlation = np.mean(correlations) if correlations else 0
        else:
            avg_correlation = 0
        
        analysis = {
            'num_traces': len(self.traces),
            'trace_length': len(mean_trace),
            'max_power': max_power,
            'min_power': min_power,
            'power_range': max_power - min_power,
            'interesting_points': len(interesting_points),
            'avg_correlation': avg_correlation,
            'mean_trace': mean_trace,
            'std_trace': std_trace,
            'variance': variance
        }
        
        print("✅ REAL data analysis complete!")
        print(f"  📈 Traces: {analysis['num_traces']}")
        print(f"  📏 Samples per trace: {analysis['trace_length']}")
        print(f"  ⚡ Power range: {analysis['min_power']:.3f} to {analysis['max_power']:.3f}")
        print(f"  🎯 Interesting points: {analysis['interesting_points']}")
        print(f"  🔗 Average correlation: {analysis['avg_correlation']:.3f}")
        
        return analysis
    
    def generate_plot(self, save_path="real_chipwhisperer_demo.png"):
        """Generate plot of real hardware data"""
        if not self.traces:
            print("❌ No traces to plot!")
            return False
        
        print("📊 Generating visualization of REAL hardware data...")
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Plot individual traces
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        for i, trace in enumerate(self.traces[:5]):
            ax1.plot(trace, alpha=0.8, color=colors[i % len(colors)], 
                    linewidth=1.2, label=f'Real Trace {i+1}')
        
        ax1.set_title('REAL ChipWhisperer Power Traces - Live Hardware Data', 
                     fontsize=16, fontweight='bold', pad=20)
        ax1.set_xlabel('Sample Number', fontsize=12)
        ax1.set_ylabel('Power Consumption (ADC units)', fontsize=12)
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.set_facecolor('#f8f9fa')
        
        # Plot statistical analysis
        if len(self.traces) > 1:
            trace_array = np.array(self.traces)
            mean_trace = np.mean(trace_array, axis=0)
            std_trace = np.std(trace_array, axis=0)
            
            ax2.plot(mean_trace, color='#2c3e50', linewidth=2.5, label='Mean Power')
            ax2.fill_between(range(len(mean_trace)), 
                           mean_trace - std_trace, 
                           mean_trace + std_trace, 
                           alpha=0.3, color='#3498db', label='±1σ Standard Deviation')
            
            # Highlight interesting points
            variance = np.var(trace_array, axis=0)
            mean_variance = np.mean(variance)
            interesting_points = np.where(variance > mean_variance * 1.5)[0]
            if len(interesting_points) > 0:
                ax2.scatter(interesting_points, mean_trace[interesting_points], 
                          color='red', s=20, alpha=0.8, label='High Variance Points')
        
        ax2.set_title('Statistical Analysis - REAL Hardware Power Patterns', 
                     fontsize=16, fontweight='bold', pad=15)
        ax2.set_xlabel('Sample Number', fontsize=12)
        ax2.set_ylabel('Power Consumption (ADC units)', fontsize=12)
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.set_facecolor('#f8f9fa')
        
        # Add title
        fig.suptitle('🔬 REAL ChipWhisperer Demo - Live Hardware Data', 
                    fontsize=18, fontweight='bold', y=0.98)
        fig.text(0.02, 0.02, 'This is REAL data captured from live ChipWhisperer hardware', 
                fontsize=12, style='italic', alpha=0.8, color='#2c3e50')
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.94, hspace=0.3)
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✅ Real hardware plot saved as {save_path}")
        return True
    
    def run_demo(self):
        """Run the complete real hardware demo"""
        print("=" * 80)
        print("    🔬 REAL ChipWhisperer Hardware Demo")
        print("=" * 80)
        
        # Connect
        if not self.connect():
            print("❌ Demo failed - cannot connect to hardware")
            return False
        
        # Test communication
        if not self.test_target_communication():
            print("❌ Demo failed - target not responding")
            return False
        
        # Capture traces
        if not self.capture_multiple_traces(5):
            print("❌ Demo failed - cannot capture traces")
            return False
        
        # Analyze
        analysis = self.analyze_traces()
        if not analysis:
            print("❌ Demo failed - analysis failed")
            return False
        
        # Generate plot
        if not self.generate_plot():
            print("❌ Demo failed - plot generation failed")
            return False
        
        print("\n" + "=" * 80)
        print("🎉 REAL HARDWARE DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("🔌 This demo used REAL ChipWhisperer hardware")
        print("📊 All data captured from live XMEGA target")
        print("📈 Check 'real_chipwhisperer_demo.png' for visualization")
        print("🎯 This shows genuine side-channel attack analysis")
        
        return True
    
    def disconnect(self):
        """Disconnect from hardware"""
        try:
            if self.scope:
                self.scope.dis()
            if self.target:
                self.target.dis()
            print("✅ Disconnected from hardware")
        except Exception as e:
            print(f"⚠ Error disconnecting: {e}")

def main():
    """Main demo function"""
    demo = RealChipWhispererDemo()
    
    try:
        success = demo.run_demo()
        if success:
            print("\n🚀 REAL hardware demo ready for presentation!")
        else:
            print("\n❌ Demo failed")
    finally:
        demo.disconnect()

if __name__ == "__main__":
    main()
