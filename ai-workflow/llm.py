"""Viên gạch dùng chung cho mọi bài tập workflow — hỗ trợ CẢ OpenAI và Anthropic.

Cài đặt:
    pip install openai anthropic      # cài cái nào bạn dùng cũng được

Đặt key (ít nhất một trong hai):
    export OPENAI_API_KEY="sk-..."
    export ANTHROPIC_API_KEY="sk-ant-..."

Chọn nhà cung cấp mặc định (không bắt buộc):
    export LLM_PROVIDER=openai         # hoặc "anthropic"
    # Nếu không đặt, tự dò: ưu tiên key nào đang có.

Cách gọi (provider-agnostic — KHÔNG cần đổi code bài tập khi chuyển nhà cung cấp):
    llm("xin chào")                    # dùng tier mặc định "balanced"
    llm("việc khó", model="strong")    # tier: cheap | balanced | strong
    llm("...", model="gpt-4o-mini")    # vẫn nhận model id cụ thể nếu muốn
"""
import os

# ---- Cấu hình tier -> model cụ thể cho từng nhà cung cấp ----
TIERS = {
    "openai": {
        "cheap":    "gpt-4o-mini",
        "balanced": "gpt-4o",
        "strong":   "gpt-4o",          # đổi sang "o3"/model suy luận nếu tài khoản bạn có
    },
    "anthropic": {
        "cheap":    "claude-haiku-4-5-20251001",
        "balanced": "claude-sonnet-4-6",
        "strong":   "claude-opus-4-8",
    },
}


def _default_provider():
    p = os.getenv("LLM_PROVIDER")
    if p:
        return p.lower()
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    return "openai"  # mặc định cuối cùng


def _infer_provider_from_model(model):
    """Nếu truyền model id cụ thể, suy ra nhà cung cấp từ tên."""
    m = model.lower()
    if m.startswith(("gpt", "o1", "o3", "o4")):
        return "openai"
    if m.startswith("claude"):
        return "anthropic"
    return None


# ---- Lazy init client để thiếu 1 key vẫn import được ----
_clients = {}


def _openai_client():
    if "openai" not in _clients:
        from openai import OpenAI
        _clients["openai"] = OpenAI()
    return _clients["openai"]


def _anthropic_client():
    if "anthropic" not in _clients:
        from anthropic import Anthropic
        _clients["anthropic"] = Anthropic()
    return _clients["anthropic"]


def llm(prompt, system="", model="cheap", provider=None,
        max_tokens=1024, temperature=1.0):
    """Gọi LLM một lần, trả về text. Dùng chung cho OpenAI và Anthropic.

    model: 'cheap' | 'balanced' | 'strong' (tier), HOẶC model id cụ thể.
    provider: 'openai' | 'anthropic'. Để None sẽ tự suy ra.
    """
    # Suy ra provider
    if provider is None:
        provider = _infer_provider_from_model(model) or _default_provider()
    provider = provider.lower()

    # Nếu là tier alias -> map sang model id; nếu đã là id cụ thể -> giữ nguyên
    model_id = TIERS.get(provider, {}).get(model, model)

    if provider == "openai":
        return _openai_call(prompt, system, model_id, max_tokens, temperature)
    elif provider == "anthropic":
        return _anthropic_call(prompt, system, model_id, max_tokens, temperature)
    raise ValueError(f"Provider không hỗ trợ: {provider}")


def _openai_call(prompt, system, model_id, max_tokens, temperature):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = _openai_client().chat.completions.create(
        model=model_id,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()


def _anthropic_call(prompt, system, model_id, max_tokens, temperature):
    msg = _anthropic_client().messages.create(
        model=model_id,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


if __name__ == "__main__":
    # Test nhanh: python llm.py
    print("Provider mặc định:", _default_provider())
    print(llm("Trả lời đúng 1 từ: thủ đô Việt Nam?", model="cheap"))
