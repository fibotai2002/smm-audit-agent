import matplotlib.pyplot as plt
import io
import numpy as np

class ChartService:
    @staticmethod
    def create_engagement_gauge(rate: float):
        """Creates a gauge chart for Engagement Rate"""
        try:
            fig, ax = plt.subplots(figsize=(4, 3), subplot_kw={'projection': 'polar'})
            
            # Normalize rate (0-10%)
            val = min(rate, 10) / 10 * np.pi
            
            # Draw semi-circle
            ax.barh(0, np.pi, color='lightgray', height=0.5, align='center')
            ax.barh(0, val, color='green' if rate > 3 else 'orange' if rate > 1 else 'red', height=0.5, align='center')
            
            ax.set_theta_zero_location('W')
            ax.set_theta_direction(-1)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines['polar'].set_visible(False)
            
            plt.text(0, -0.2, f"{rate}%", ha='center', va='center', fontsize=20, fontweight='bold')
            plt.title("Engagement Rate", y=1.1)
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            plt.close()
            return buf
        except Exception as e:
            print(f"Chart Error (Gauge): {e}")
            return None

    @staticmethod
    def create_post_distribution(video_count: int, photo_count: int):
        """Creates a pie chart for Video vs Photo posts"""
        try:
            if video_count == 0 and photo_count == 0:
                return None
            
            labels = ['Video (Reels)', 'Rasm/Carousel']
            sizes = [video_count, photo_count]
            colors = ['#ff006e', '#3a86ff'] # Pink for IG/Reels, Blue for Photo
            
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.axis('equal') 
            plt.title("Kontent Turi")
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            plt.close()
            return buf
        except Exception as e:
            print(f"Chart Error (Pie): {e}")
            return None

    @staticmethod
    def create_growth_chart(views_data: list):
        """Creates a line chart for Views Growth (Example data)"""
        try:
            if not views_data:
                return None
                
            fig, ax = plt.subplots(figsize=(5, 3))
            ax.plot(views_data, marker='o', linestyle='-', color='purple')
            ax.set_title("Ko'rishlar Dinamikasi (Oxirgi 10 post)")
            ax.grid(True, linestyle='--', alpha=0.6)
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            plt.close()
            return buf
        except Exception as e:
            print(f"Chart Error (Line): {e}")
            return None
