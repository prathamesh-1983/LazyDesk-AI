# 🦥 LazyDesk AI: A Local Productivity Agent That Does the Tedious Work for You

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 3: Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19)*

## What I Built

I built **LazyDesk AI**, a local-first productivity assistant designed to reduce repetitive digital work and help people spend less time on tasks they keep putting off.

We all have those little tasks that consume more time than they should: summarizing long notes, turning messy thoughts into actionable tasks, and organizing files scattered across our computers.

LazyDesk AI helps automate these tasks using an open-weight AI model running locally through Ollama.

The project includes three core features:

- ✨ **AI Text Summarizer:** Turns lengthy notes and documents into concise summaries.
- ✅ **Smart Task Extractor:** Converts unstructured notes and brain dumps into actionable Markdown checklists.
- 🗂️ **File Organizer:** Scans a selected folder, categorizes files by type, and previews proposed file moves before the user approves them.

The file organizer does not delete files or overwrite existing destinations. Users can review proposed changes before applying them.

The goal is simple: **let AI handle repetitive work so people can focus on what matters.**

## Demo

- **Demo Video:** https://drive.google.com/file/d/1ECIqXGFzowDATrzhGO45NrCCvIy4UBI2/view?usp=sharing

The application runs locally with Streamlit and Ollama. A public demo or video should be added here once it has been created and tested.

## Code

**GitHub Repository:** https://github.com/prathamesh-1983/LazyDesk-AI

**Tech stack:**

- Python — application logic and file processing
- Streamlit — interactive web interface
- Ollama — local model inference
- Open-weight language model — text summarization and task extraction
- Pytest — automated tests for file organization behavior

The project is organized into separate modules for the user interface, AI communication, text-processing tasks, file organization, and utility functions.

The repository also includes a README with setup instructions, a dependency list, an MIT license, and tests for key file-organizer behaviors.

## How I Built It

I built LazyDesk AI using Python and Streamlit, with Ollama providing access to a locally running open-weight language model.

Instead of relying on a hosted AI API, the application sends text-generation requests to the configured Ollama server.

Here is how the main components work:

**1. Local AI communication**

The `lazydesk/llm.py` module communicates with Ollama through its HTTP API. It handles model requests, connection problems, timeouts, and helpful error messages.

**2. Text summarization**

The text assistant accepts user-provided text and asks the local model to create a concise summary, an executive summary, or a list of key points and decisions.

**3. Task extraction**

The task extractor transforms brain dumps into Markdown checklists. It instructs the model not to invent owners or deadlines that were not included in the original notes.

**4. Safe file organization**

The file organizer scans top-level files in a selected directory, identifies file types, and proposes category folders such as Documents, Images, Spreadsheets, Code, and Archives.

Before moving files, LazyDesk AI displays a preview. The user must explicitly approve the changes. The organizer skips existing destinations and does not delete files.

**5. Testing and reliability**

I included automated tests for file categorization, directory scanning, planned file moves, and protection against overwriting an existing destination.

To run the project locally, install the dependencies, install Ollama, download a compatible model, and launch the application with:

```bash
pip install -r requirements.txt
ollama pull qwen2.5:3b
streamlit run app.py
```

The selected model must be supported by the installed Ollama version and compatible with the computer's available resources.

## Why Does Open Innovation Matter?

Open innovation matters because productivity tools should give users more control over their workflows, their data, and the technology they depend on.

By building LazyDesk AI around a locally running open-weight model, I explored several advantages:

**Privacy and control:** When Ollama runs on the user's own computer, prompts can be processed locally rather than sent to a third-party AI API. This is particularly useful when working with personal notes and documents.

**Offline potential:** After downloading the model, supported AI tasks can run without an internet connection, provided the local application and model are available.

**Freedom to experiment:** Users can switch compatible models, adjust prompts, and customize the application without rebuilding the entire project around a proprietary API.

**Reduced API dependence:** Local inference avoids per-request charges from a hosted AI API, although hardware, electricity, and model-download costs still matter.

**Accessible development:** Open tools such as Python, Streamlit, Ollama, and Pytest make it possible for independent developers to experiment with AI-powered applications.

A closed API can be convenient, and it may provide stronger results for some tasks. However, a local-first approach offers a different set of benefits: greater control, customization, and the opportunity to keep processing on the user's own machine.

For LazyDesk AI, open innovation is not just a technology choice. It is part of the project's goal of making useful automation more accessible.

## My Agent Session

I developed the project by breaking the productivity problem into smaller features: summarization, task extraction, and file organization.

**DevRelay Session:** [Add your DevRelay session URL, if available]

This section is optional. If you did not save a DevRelay session, you can remove it before publishing.

## The Lazy Payoff

The idea behind LazyDesk AI is to reduce the effort involved in small, repetitive digital tasks.

Instead of manually condensing long notes, users can generate a summary. Instead of sorting through an unstructured brain dump, they can create an actionable checklist. Instead of moving files one by one, they can review a proposed organization plan and approve the moves.

I have not yet established a measured time-saving figure, so I will not claim a specific number of minutes saved. Measuring the time taken to complete these tasks manually versus using LazyDesk AI would be a useful next step.

The bigger idea is that small improvements in everyday workflows can add up over time.

**Slow and steady wins: let the computer handle the repetitive work while you focus on the meaningful work.** 🦥

## Prize Categories

This submission focuses on the main **Slow and Steady** challenge.

[Add any eligible partner prize categories here, if applicable, or remove this section if you are not entering any.]

---

Built for the Hacktoberfest Open-Source AI Challenge Week 3.

#hacktoberfest #hf26challenge #opensource #AI #Python #Ollama #Streamlit #Productivity
