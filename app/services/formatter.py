import json

class Formatter:
    @staticmethod
    def format_report_to_messages(report: dict, instagram_url: str = "N/A", telegram_url: str = "N/A") -> list[str]:
        """Splits the report into Telegram-friendly text chunks"""
        messages = []
        
        # 1. Quick Audit & Positioning
        quick_audit = "\n🔹 ".join(report.get("quick_audit", []))
        positioning = report.get("positioning_analysis", {}).get("details", "")
        
        msg1 = f"🔥 **TEZKOR AUDIT**\n\n🔹 {quick_audit}\n\n"
        msg1 += f"🎯 **POZITSIYALASH**\n\n{positioning}"
        messages.append(msg1)

        # 2. Strategy
        content_pillars = "\n📌 ".join(report.get("content_pillars", []))
        hooks = "\n🪝 ".join(report.get("hooks_strategy", []))
        
        msg2 = f"📈 **KONTENT STRATEGIYASI**\n\n**Mavzular (Pillars):**\n📌 {content_pillars}\n\n**Ilgaklar (Hooks):**\n🪝 {hooks}"
        messages.append(msg2)

        # 3. Action Plan (Next 7 Days)
        action_plan = report.get("next_7_days_action_plan", [])
        plan_text = ""
        if isinstance(action_plan, list):
             plan_text = "\n🚀 ".join([str(item) for item in action_plan])
        else:
             plan_text = str(action_plan)

        msg3 = f"🚀 **7 KUNLIK HARAKAT REJASI**\n\n🚀 {plan_text}"
        messages.append(msg3)
        
        # 4. KPI & Risks
        risks = "\n⚠ ".join(report.get("risks", []))
        kpis = report.get("kpi_targets", {}).get("details", "")

        msg4 = f"📊 **KPI MAQSADLARI**\n\n{kpis}\n\n⚠ **XAVFLAR**\n\n⚠ {risks}"
        messages.append(msg4)

        return messages
