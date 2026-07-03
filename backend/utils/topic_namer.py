from groq import Groq
from dotenv import load_dotenv
import os
import time  # it will pause the program when rate limit exceeds

load_dotenv()  # load the value to memory

client = Groq(api_key=os.getenv("GROQ_API_KEY")) # groq is creating the connection

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a topic-naming assistant for a document knowledge base.
Rules:
1. Read the cluster excerpts provided and assign each a short, specific 2-4 word name.
2. Every name must be genuinely distinct from the others — never reuse or lightly reword the same name for two different clusters.
3. Base names only on the actual content shown — never invent topics not present in the excerpts.
4. Follow the exact output format requested. No extra commentary, no markdown, no numbering beyond what's asked."""


def generate_all_topic_names(cluster_samples: dict, retries=3) -> dict:
    cluster_ids = list(cluster_samples.keys())

    sections = []
    for cid in cluster_ids:
        sample_text = "\n".join(cluster_samples[cid][:3])
        sections.append(f"--- Cluster {cid} ---\n{sample_text}")

    combined = "\n\n".join(sections)

    prompt = f"""
    Below are excerpts from {len(cluster_ids)} different topic clusters found in a document.

    For EACH cluster, give a short topic name (2-4 words).
    IMPORTANT: All names must be DISTINCT from each other — do not reuse
    the same or near-identical name for two different clusters, even if
    they seem related. If two clusters are similar, make the names more
    specific to highlight what's different between them.

    Respond in this EXACT format, one line per cluster, no extra text:
    Cluster <id>: <topic name>

    Clusters:
    {combined}
    """

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200,
            )
            raw = response.choices[0].message.content.strip()

            topic_names = {}
            for line in raw.splitlines():
                line = line.strip()
                if not line.lower().startswith("cluster"):
                    continue
                try:
                    prefix, name = line.split(":", 1)
                    cid_str = prefix.lower().replace("cluster", "").strip()
                    cid = int(cid_str)
                    topic_names[cid] = name.strip()
                except (ValueError, IndexError):
                    continue

            # Fallback for any cluster the model missed
            for cid in cluster_ids:
                if cid not in topic_names:
                    topic_names[cid] = f"Topic {cid}"

            # Safety net: deduplicate, in case the model still produced duplicates
            seen = {}
            for cid in cluster_ids:
                name = topic_names[cid]
                if name in seen:
                    seen[name] += 1
                    topic_names[cid] = f"{name} ({seen[name]})"
                else:
                    seen[name] = 1

            return topic_names

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate_limit" in error_msg.lower():
                wait = 30 * (attempt + 1)
                print(f"Rate limited. Waiting {wait}s before retry {attempt + 1}/{retries}...")
                time.sleep(wait)
            else:
                raise e

    return {cid: f"Topic {cid}" for cid in cluster_ids}