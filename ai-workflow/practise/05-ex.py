import sys
from pathlib import Path
import concurrent.futures

sys.path.append(str(Path(__file__).parent.parent))
from llm import llm

def orchestrator(subject):
    prompt = f"Tôi đang muốn nghiên cứu về chủ đề {subject}, chỉ trả về duy nhấtkết quả một danh sách các mục con cần nghiên cứu của chủ đề đó, mỗi mục con là một dòng"
    result = llm(prompt, model="cheap", provider="openai")
    return result.splitlines()

def research(subject, item):
    prompt = f"Tôi đang muốn nghiên cứu về chủ đề {subject}, hãy viết cho tôi một đoạn văn ngắn về mục con {item} của chủ đề đó"
    result = llm(prompt, model="cheap", provider="openai")
    return result

def synthesize(subject, research_results):
    full_research_results = "\n ".join(research_results)
    return full_research_results

def pipeline(subject):
    research_items = orchestrator(subject)
    research_results = []

    print(f"Research items for '{subject}':")
    for item in research_items:
        print(f"- {item}")

    # run in concurrent
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(research, subject, item): item for item in research_items}
        for future in concurrent.futures.as_completed(futures):
            item = futures[future]
            try:
                result = future.result()
                #add result to research_results as order of research_items
                index = research_items.index(item)
                research_results.insert(index, result)


                if len(research_results) == len(research_items):
                    synthesized_result = synthesize(subject, research_results)
                    print(f"\nSynthesized research results for '{subject}':\n{synthesized_result}")
            except Exception as e:
                print(f"Error processing '{item}': {e}")


if __name__ == "__main__":
    subject = "Trí tuệ nhân tạo"
    pipeline(subject)
