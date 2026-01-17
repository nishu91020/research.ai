'''Research Scholar Agent
Proficient in researching any topics from varied fields like medicine, technology,
Physics, Mathematics, Computer Science, Quantitative Biology, Quantitative Finance, 
Statistics, Electrical Engineering, and Economics. Performs in-depth analysis leveraging 
various research websites and creates educational content.
'''

'''
steps for building a langgraph workflow:
1. Define the state schema using TypedDict.
2. Initialize the LLM (AzureChatOpenAI).
3. Define tools
5. define each state function as node
6. build graph - add nodes, edges
'''

import os
# Disable langsmith tracing before any langchain imports
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_ENDPOINT"] = ""
os.environ["LANGCHAIN_API_KEY"] = ""

from langgraph.graph import StateGraph, END
from typing import Dict, List, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from dotenv import load_dotenv
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.azure_responses_api import ResponsesAPIChatModel

# Load environment variables from .env.local - only if file exists (local dev)
env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Define state
class AgentState(TypedDict):
    topic: str
    field: str
    fetched_data: Dict[str, list[Dict]]
    selected_artices: list[Dict]
    summary: str
    article: str

# Lazy LLM initialization to avoid import-time errors
_llm = None

def get_llm():
    """Get or initialize the LLM instance"""
    global _llm
    if _llm is None:
        _llm = ResponsesAPIChatModel(model="gpt-4.1")
    return _llm

# ==================== Tools ====================

@tool
def medicine_bio_lifescience_research(topic: str) -> Dict[str, List[Dict]]:
    """Research the given topic on medical or life science"""
    results = {}
    topicSearch = topic.replace(" ", "+")
    
    # bioRxiv scrape
    try:
        url = f"https://www.biorxiv.org/search/{topicSearch}"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        articles = []
        for item in soup.find_all("li", class_="search-result"):
            title = item.find("span", class_="highwire-cite-title").text.strip() if item.find("span", class_="highwire-cite-title") else ""
            abstract = item.find("div", class_="highwire-cite-metadata").text.strip() if item.find("div", class_="highwire-cite-metadata") else ""
            url = "https://www.biorxiv.org" + item.find("a")["href"] if item.find("a") else ""
            articles.append({"title": title, "abstract": abstract, "url": url})
        results["bioRxiv"] = articles[:10]
    except Exception as e:
        results["bioRxiv"] = [{"error": str(e)}]
    
    # medRxiv scrape
    try:
        url = f"https://www.medrxiv.org/search/{topicSearch}"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        articles = []
        for item in soup.find_all("li", class_="search-result"):
            title = item.find("span", class_="highwire-cite-title").text.strip() if item.find("span", class_="highwire-cite-title") else ""
            abstract = item.find("div", class_="highwire-cite-metadata").text.strip() if item.find("div", class_="highwire-cite-metadata") else ""
            url = "https://www.medrxiv.org" + item.find("a")["href"] if item.find("a") else ""
            articles.append({"title": title, "abstract": abstract, "url": url})
        results["medRxiv"] = articles[:10]
    except Exception as e:
        results["medRxiv"] = [{"error": str(e)}]
    
    # PubMed scrape
    try:
        url = f"https://pubmed.ncbi.nlm.nih.gov/?term={topicSearch}"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        articles = []
        for item in soup.find_all("li", class_="search-result"):
            title = item.find("span", class_="highwire-cite-title").text.strip() if item.find("span", class_="highwire-cite-title") else ""
            abstract = item.find("div", class_="highwire-cite-metadata").text.strip() if item.find("div", class_="highwire-cite-metadata") else ""
            url = "https://www.pubmed.org" + item.find("a")["href"] if item.find("a") else ""
            articles.append({"title": title, "abstract": abstract, "url": url})
        results["PubMed"] = articles[:10]
    except Exception as e:
        results["PubMed"] = [{"error": str(e)}]
    
    return results

@tool
def socialScience_law_humanities_research(topic: str) -> Dict[str, List[Dict]]:
    """Research the given topic on social science, law and humanities"""
    results = {"SSRN": []}
    
    query = quote(topic.replace(" ", "+"))
    url = f"https://papers.ssrn.com/searchresults.cfm?term={query}"
    
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        if resp.status_code != 200:
            raise ValueError(f"HTTP {resp.status_code}: Unable to fetch page")
        
        soup = BeautifulSoup(resp.text, "html.parser")
        result_items = soup.find("ol", class_="searchResults")
        if not result_items:
            raise ValueError("No search results found or page structure changed")
        
        for item in result_items.find_all("li")[:10]:
            title_elem = item.find("h3")
            title = title_elem.find("a").text.strip() if title_elem and title_elem.find("a") else "N/A"
            
            authors_div = item.find("div", class_="authors")
            authors = authors_div.text.strip() if authors_div else "N/A"
            
            abstract_div = item.find("div", class_="abstract")
            abstract = abstract_div.text.strip()[:500] + "..." if abstract_div and abstract_div.text.strip() else "N/A"
            
            date_span = item.find("span", class_="date")
            pub_date = date_span.text.strip() if date_span else "N/A"
            
            link = title_elem.find("a")["href"] if title_elem and title_elem.find("a") else ""
            full_url = "https://papers.ssrn.com" + link if link.startswith("/") else link
            
            results["SSRN"].append({
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "pub_date": pub_date,
                "url": full_url
            })
        
        if not results["SSRN"]:
            results["SSRN"] = [{"note": "No relevant papers found for this query."}]
    
    except Exception as e:
        results["SSRN"] = [{"error": str(e)}]
    
    return results

@tool
def multi_disciplinary_research(topic: str) -> Dict[str, List[Dict]]:
    """Research the given topic across multiple disciplines"""
    results = {"arXiv": [], "SpringerOpen": []}
    query = topic.replace(" ", "+")
    
    # arXiv search
    try:
        url = f"https://arxiv.org/search/?query={query}&source=header&searchtype=all"
        res = requests.get(url)
        if res.status_code != 200:
            raise ValueError(f"arXiv HTTP {res.status_code}: Unable to fetch page")
        
        soup = BeautifulSoup(res.text, "html.parser")
        articles = soup.find_all("li", class_="arxiv-result")[:10]
        for article in articles:
            title_elem = article.find("p", class_="title")
            title = title_elem.text.strip() if title_elem else "N/A"
            
            authors_elem = article.find("p", class_="authors")
            authors = authors_elem.text.replace("Authors:", "").strip() if authors_elem else "N/A"
            
            abstract_elem = article.find("p", class_="abstract")
            abstract = abstract_elem.text.strip()[:500] + "..." if abstract_elem and abstract_elem.text.strip() else "N/A"
            
            date_elem = article.find("p", class_="is-size-7")
            pub_date = date_elem.text.split(";")[0].strip() if date_elem else "N/A"
            
            url_elem = article.find("p", class_="list-title").find("a")
            url = url_elem["href"] if url_elem else ""
            
            results["arXiv"].append({
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "pub_date": pub_date,
                "url": url
            })
        
        if not articles:
            results["arXiv"].append({"note": "No relevant papers found for this query on arXiv."})
    
    except Exception as e:
        results["arXiv"] = [{"error": str(e)}]
    
    # SpringerOpen search
    springer_url = f"https://www.springeropen.com/search?query={query}&searchType=publisherSearch"
    try:
        resp = requests.get(springer_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        if resp.status_code != 200:
            raise ValueError(f"SpringerOpen HTTP {resp.status_code}: Unable to fetch page")
        
        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.find_all("div", class_="c-search-result__body")[:10]
        for article in articles:
            title_elem = article.find("h3", class_="c-search-result__title")
            title = title_elem.find("a").text.strip() if title_elem and title_elem.find("a") else "N/A"
            
            authors_elem = article.find("p", class_="c-search-result__meta")
            authors = authors_elem.text.split("|")[0].strip() if authors_elem else "N/A"
            
            abstract_elem = article.find("p", class_="c-search-result__abstract")
            abstract = abstract_elem.text.strip()[:500] + "..." if abstract_elem and abstract_elem.text.strip() else "N/A"
            
            date_elem = article.find("p", class_="c-search-result__meta")
            pub_date = date_elem.text.split("|")[-1].strip() if date_elem else "N/A"
            
            url_elem = article.find("h3", class_="c-search-result__title").find("a")
            url = "https://www.springeropen.com" + url_elem["href"] if url_elem else ""
            
            results["SpringerOpen"].append({
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "pub_date": pub_date,
                "url": url
            })
        
        if not articles:
            results["SpringerOpen"].append({"note": "No relevant papers found for this query on SpringerOpen."})
    
    except Exception as e:
        results["SpringerOpen"] = [{"error": str(e)}]
    
    return results

# ==================== Node Functions ====================

# 1. Classify field
classify_prompt = ChatPromptTemplate.from_template("""Classify the topic '{topic}' into fields like Physics, Mathematics, 
Computer Science, Quantitative Biology, Quantitative Finance, Statistics, Electrical Engineering, and Economics, Biology and Life Sciences, 
Medicine and Health Sciences, Social Sciences, Humanities, Law, Economics, and Business, Biomedical and Life Sciences, Science, Technology, Medicine.
output only the field name""")

def classify_field(state: AgentState) -> AgentState:
    classify_chain = classify_prompt | get_llm()
    field = classify_chain.invoke({"topic": state["topic"]}).content.strip().lower()
    state["field"] = field
    return state

# 2 & 3. Fetch data
def fetch_data(state: AgentState) -> AgentState:
    print(f"Fetching data for field: {state['field']}")
    field = state.get("field", "").lower()
    if any(x in field for x in ["medicine", "health sciences", "biology", "life sciences", "biomedical"]):
        state["fetched_data"] = medicine_bio_lifescience_research.invoke({"topic": state["topic"]})
    elif any(x in field for x in ["social sciences", "humanities", "law", "economics", "business"]):
        state["fetched_data"] = socialScience_law_humanities_research.invoke({"topic": state["topic"]})
    else:
        state["fetched_data"] = multi_disciplinary_research.invoke({"topic": state["topic"]})
    return state

# 4. Select relevant articles
select_prompt = ChatPromptTemplate.from_template(
    "From these articles: {articles}\nSelect the top 3 most relevant to '{topic}'. Output as JSON list: [{{title, url, reason}}]"
)

def select_relevant(state: AgentState) -> AgentState:
    select_chain = select_prompt | get_llm()
    all_articles = []
    for source, article in state["fetched_data"].items():
        if isinstance(article, list):
            all_articles.extend(article)
    if all_articles:
        selected = select_chain.invoke({"articles": all_articles, "topic": state["topic"]}).content
        try:
            state["selected_artices"] = eval(selected)
        except:
            state["selected_artices"] = all_articles[:3]
    else:
        state["selected_artices"] = []
    return state

# 5. Summarize findings
summary_prompt = ChatPromptTemplate.from_template("""Based on the articles: {articles}

Summarize the key findings on the topic '{topic}' in a clear and concise manner.

Format using Markdown:
- Use **bold** for key terms
- Use bullet points for listing findings
- Keep it well-structured and informative""")

def summarise(state: AgentState) -> AgentState:
    summary_chain = summary_prompt | get_llm()
    state["summary"] = summary_chain.invoke({"articles": state["selected_artices"], "topic": state["topic"]}).content
    return state

# 6. Draft article
article_draft_prompt = ChatPromptTemplate.from_template("""Draft a comprehensive article on the topic '{topic}' using the summary: {summary}

Format the article with proper Markdown syntax:
- Use # for main title
- Use ## for major sections
- Use ### for subsections
- Use **bold** for emphasis
- Use bullet points with - or *
- Use numbered lists where appropriate
- Include relevant hashtags at the end

Make it well-structured, informative, and easy to read.""")

def draft(state: AgentState) -> AgentState:
    article_draft_chain = article_draft_prompt | get_llm()
    state["article"] = article_draft_chain.invoke({"summary": state["summary"], "topic": state["topic"]}).content
    return state

# ==================== Graph Construction ====================

def build_research_graph():
    """Build and return the research workflow graph"""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("classify", classify_field)
    workflow.add_node("fetch", fetch_data)
    workflow.add_node("select", select_relevant)
    workflow.add_node("summarise", summarise)
    workflow.add_node("draft", draft)
    
    # Set entry point and add edges
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "fetch")
    workflow.add_edge("fetch", "select")
    workflow.add_edge("select", "summarise")
    workflow.add_edge("summarise", "draft")
    workflow.add_edge("draft", END)
    
    return workflow.compile()

# Create the compiled graph
graph = build_research_graph()

def run_research(topic: str) -> dict:
    """Run the research workflow for a given topic"""
    print(f"Running research for topic: {topic}")
    initial_state = {
        "topic": topic,
        "field": "",
        "fetched_data": {},
        "selected_artices": [],
        "summary": "",
        "article": "",
    }
    return graph.invoke(initial_state)
