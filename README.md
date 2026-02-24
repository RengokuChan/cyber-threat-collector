# Cyber-Threat-Collector

## Description
Cyber-Threat-Collector is a professional Discord bot and Python-based automation tool designed for real-time cybersecurity monitoring. It aggregates and parses over 25 global threat intelligence feeds (including CERT-FR, ANSSI, and NIST) to deliver critical security alerts directly to a dedicated Discord channel.

This project streamlines threat intelligence by centralizing fragmented security feeds into a single, actionable Discord notification stream.

## Key Features
* Discord Integration: Automated delivery of threat alerts to Discord servers using discord.py.
* Multi-Source Aggregation: Seamlessly parses RSS/Atom feeds from major cybersecurity authorities and CERTs.
* Intelligent Deduplication: Utilizes a local SQLite persistence layer to ensure zero redundant notifications.
* Asynchronous Engine: Built with asyncio for high-performance, non-blocking operations.
* Dockerized Architecture: Fully containerized for secure, portable, and consistent deployment.

## DevOps and Security Specs
* Containerization: Uses a lightweight python:slim Docker image to minimize the attack surface.
* Environment Isolation: The bot runs in a restricted container, preventing direct access to the host system.
* Secret Management: Sensitive Discord tokens are managed via environment variables and excluded from version control.

## Quick Start (Docker)

1. Clone the repository:
   ```bash
   git clone [https://github.com/RengokuChan/cyber-threat-collector.git](https://github.com/RengokuChan/cyber-threat-collector.git)
   cd cyber-threat-collector
