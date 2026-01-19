"""
Marketing Plan Export Utilities

Converts MarketingTeamOutput to various formats:
- Markdown
- Plain text (copy-friendly)
- Google Docs
"""
from typing import Optional
from datetime import datetime

from models.marketing import (
    MarketingTeamOutput,
    CampaignStrategy,
    MidjourneyPrompt,
    CampaignConcept,
    MarketResearch
)
from lib.logging_config import logger


def strategy_to_markdown(strategy: CampaignStrategy) -> str:
    """Convert CampaignStrategy to formatted Markdown"""
    lines = []
    
    # Header
    lines.append(f"# Marketing Campaign: {strategy.product_name}")
    lines.append(f"**Target Market:** {strategy.target_market}")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    
    # Market Research
    lines.append("## 📊 Market Research")
    lines.append("")
    
    research = strategy.research
    lines.append("### Target Demographics")
    for item in research.target_demographics:
        lines.append(f"- {item}")
    lines.append("")
    
    lines.append("### Consumer Behaviors")
    for item in research.consumer_behaviors:
        lines.append(f"- {item}")
    lines.append("")
    
    lines.append("### Preferred Channels")
    for item in research.preferred_channels:
        lines.append(f"- {item}")
    lines.append("")
    
    lines.append("### Competitor Insights")
    for item in research.competitor_insights:
        lines.append(f"- {item}")
    lines.append("")
    
    lines.append("### Market Opportunities")
    for item in research.market_opportunities:
        lines.append(f"- {item}")
    lines.append("")
    
    # Campaign Concepts
    lines.append("## 💡 Campaign Concepts")
    lines.append("")
    
    for i, concept in enumerate(strategy.concepts, 1):
        is_recommended = concept.name == strategy.recommended_concept
        rec_badge = " ⭐ RECOMMENDED" if is_recommended else ""
        lines.append(f"### Concept {i}: {concept.name}{rec_badge}")
        lines.append("")
        lines.append(f"**Theme:** {concept.theme}")
        lines.append(f"**Target Audience:** {concept.target_audience}")
        lines.append(f"**Visual Direction:** {concept.visual_direction}")
        lines.append("")
        
        lines.append("**Key Messages:**")
        for msg in concept.key_messaging:
            lines.append(f"- {msg}")
        lines.append("")
        
        lines.append("**Channel Strategy:**")
        for channel in concept.channel_strategy:
            lines.append(f"- {channel}")
        lines.append("")
        
        lines.append("**Expected Outcomes:**")
        for outcome in concept.expected_outcomes:
            lines.append(f"- {outcome}")
        lines.append("")
    
    # Image Prompts
    lines.append("## 🎨 Midjourney Image Prompts")
    lines.append("")
    
    for i, prompt in enumerate(strategy.image_prompts, 1):
        lines.append(f"### Image {i}")
        lines.append("")
        lines.append("**Prompt:**")
        lines.append(f"```")
        lines.append(prompt.to_prompt_string())
        lines.append(f"```")
        lines.append("")
        lines.append(f"- **Subject:** {prompt.subject}")
        lines.append(f"- **Environment:** {prompt.environment}")
        lines.append(f"- **Style:** {prompt.style.value}")
        lines.append(f"- **Lighting:** {prompt.lighting}")
        lines.append(f"- **Mood:** {prompt.mood}")
        lines.append(f"- **Colors:** {', '.join(prompt.color_palette)}")
        lines.append("")
    
    # Timeline & Budget
    lines.append("## 📅 Implementation")
    lines.append("")
    lines.append(f"**Timeline:** {strategy.timeline_weeks} weeks")
    lines.append("")
    lines.append("**Budget Allocation:**")
    for channel, pct in strategy.budget_allocation.items():
        lines.append(f"- {channel.title()}: {pct}%")
    lines.append("")
    
    return "\n".join(lines)


def strategy_to_plain_text(strategy: CampaignStrategy) -> str:
    """Convert CampaignStrategy to plain text (no markdown formatting)"""
    lines = []
    
    # Header
    lines.append(f"MARKETING CAMPAIGN: {strategy.product_name.upper()}")
    lines.append(f"Target Market: {strategy.target_market}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("=" * 60)
    
    # Market Research
    lines.append("")
    lines.append("MARKET RESEARCH")
    lines.append("-" * 40)
    
    research = strategy.research
    lines.append("")
    lines.append("Target Demographics:")
    for item in research.target_demographics:
        lines.append(f"  • {item}")
    
    lines.append("")
    lines.append("Consumer Behaviors:")
    for item in research.consumer_behaviors:
        lines.append(f"  • {item}")
    
    lines.append("")
    lines.append("Preferred Channels:")
    for item in research.preferred_channels:
        lines.append(f"  • {item}")
    
    lines.append("")
    lines.append("Competitor Insights:")
    for item in research.competitor_insights:
        lines.append(f"  • {item}")
    
    lines.append("")
    lines.append("Market Opportunities:")
    for item in research.market_opportunities:
        lines.append(f"  • {item}")
    
    # Campaign Concepts
    lines.append("")
    lines.append("=" * 60)
    lines.append("")
    lines.append("CAMPAIGN CONCEPTS")
    lines.append("-" * 40)
    
    for i, concept in enumerate(strategy.concepts, 1):
        is_recommended = concept.name == strategy.recommended_concept
        rec_badge = " [RECOMMENDED]" if is_recommended else ""
        lines.append("")
        lines.append(f"CONCEPT {i}: {concept.name}{rec_badge}")
        lines.append("")
        lines.append(f"Theme: {concept.theme}")
        lines.append(f"Target Audience: {concept.target_audience}")
        lines.append(f"Visual Direction: {concept.visual_direction}")
        lines.append("")
        lines.append("Key Messages:")
        for msg in concept.key_messaging:
            lines.append(f"  • {msg}")
        lines.append("")
        lines.append("Channel Strategy:")
        for channel in concept.channel_strategy:
            lines.append(f"  • {channel}")
        lines.append("")
        lines.append("Expected Outcomes:")
        for outcome in concept.expected_outcomes:
            lines.append(f"  • {outcome}")
    
    # Image Prompts
    lines.append("")
    lines.append("=" * 60)
    lines.append("")
    lines.append("MIDJOURNEY IMAGE PROMPTS")
    lines.append("-" * 40)
    
    for i, prompt in enumerate(strategy.image_prompts, 1):
        lines.append("")
        lines.append(f"IMAGE {i}:")
        lines.append(prompt.to_prompt_string())
        lines.append("")
        lines.append(f"  Subject: {prompt.subject}")
        lines.append(f"  Environment: {prompt.environment}")
        lines.append(f"  Style: {prompt.style.value}")
        lines.append(f"  Lighting: {prompt.lighting}")
        lines.append(f"  Mood: {prompt.mood}")
        lines.append(f"  Colors: {', '.join(prompt.color_palette)}")
    
    # Timeline & Budget
    lines.append("")
    lines.append("=" * 60)
    lines.append("")
    lines.append("IMPLEMENTATION")
    lines.append("-" * 40)
    lines.append("")
    lines.append(f"Timeline: {strategy.timeline_weeks} weeks")
    lines.append("")
    lines.append("Budget Allocation:")
    for channel, pct in strategy.budget_allocation.items():
        lines.append(f"  • {channel.title()}: {pct}%")
    
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def output_to_markdown(output: MarketingTeamOutput) -> str:
    """Convert full MarketingTeamOutput to Markdown"""
    lines = []
    
    # Main strategy content
    lines.append(strategy_to_markdown(output.strategy))
    
    # Execution notes
    if output.execution_notes:
        lines.append("---")
        lines.append("")
        lines.append("## 📝 Execution Notes")
        lines.append("")
        for note in output.execution_notes:
            lines.append(f"- {note}")
        lines.append("")
    
    # Next steps
    if output.next_steps:
        lines.append("## ✅ Next Steps")
        lines.append("")
        for step in output.next_steps:
            lines.append(f"- [ ] {step}")
        lines.append("")
    
    # Footer
    lines.append("---")
    lines.append(f"*Task ID: {output.task_id} | Status: {output.status}*")
    
    return "\n".join(lines)


def output_to_plain_text(output: MarketingTeamOutput) -> str:
    """Convert full MarketingTeamOutput to plain text"""
    lines = []
    
    # Main strategy content
    lines.append(strategy_to_plain_text(output.strategy))
    
    # Execution notes
    if output.execution_notes:
        lines.append("")
        lines.append("EXECUTION NOTES:")
        for note in output.execution_notes:
            lines.append(f"  • {note}")
    
    # Next steps
    if output.next_steps:
        lines.append("")
        lines.append("NEXT STEPS:")
        for step in output.next_steps:
            lines.append(f"  [ ] {step}")
    
    # Footer
    lines.append("")
    lines.append(f"Task ID: {output.task_id} | Status: {output.status}")
    
    return "\n".join(lines)
