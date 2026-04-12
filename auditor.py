import json

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def audit_health(metrics, incomplete_data=False):
    config = load_config()
    flags = []
    
    if metrics['unit_session_pct'] < config['target_unit_session_pct']:
        flags.append(f"CONV_LOW: {metrics['unit_session_pct']}% (Target: {config['target_unit_session_pct']}%)")
    
    if metrics['tacos_pct'] > config['max_tacos_pct']:
        flags.append(f"TACOS_HIGH: {metrics['tacos_pct']}% (Max: {config['max_tacos_pct']}%)")
        
    if metrics['return_pct'] > config['max_return_pct']:
        flags.append(f"REFUND_HIGH: {metrics['return_pct']}% (Max: {config['max_return_pct']}%)")

    # Compact JSON for Gemini Flash (Token Efficient)
    data_payload = {
        "metrics": metrics,
        "config": config,
        "violations": flags,
        "data_status": "partially_complete" if incomplete_data else "full"
    }

    llm_prompt = f"""
    AI FINANCE AUDITOR TASK:
    Structure: {json.dumps(data_payload, separators=(',', ':'))}
    
    INSTRUCTIONS:
    1. Write a 2-sentence executive summary.
    2. If partially_complete, note "DATA GAP DETECTED" first.
    3. Suggest exactly one brief operational step if violations exist.
    """
    
    return {
        "status": "Warning" if flags or incomplete_data else "Healthy",
        "flags": flags,
        "llm_prompt": llm_prompt.strip(),
        "incomplete_data": incomplete_data
    }
