---
title: "Data Processing Agreement Template"
department: "legal"
doc_type: "legal"
created: "2025-02-20"
sensitivity: "public"
---

# Data Processing Agreement

## 1. Definitions

"Data Controller" means the Customer. "Data Processor" means our company. "Personal Data" has the meaning given in the GDPR. "Sub-processor" means any third party engaged by the Processor to process Personal Data on behalf of the Controller.

## 2. Scope of Processing

The Processor shall process Personal Data only to the extent necessary to provide the Services described in the Master Subscription Agreement. Processing activities include: ingestion and indexing of documents from Customer's connected data sources, generation of embeddings, storage of document content and metadata, and retrieval of relevant context in response to queries.

## 3. Data Security

The Processor implements appropriate technical and organizational measures including:
- Encryption at rest (AES-256) and in transit (TLS 1.3)
- Logical tenant isolation in multi-tenant environment
- Access controls with principle of least privilege
- Regular penetration testing (annually) and vulnerability scanning (weekly)
- SOC 2 Type II certified infrastructure

## 4. Sub-processors

Current sub-processors:
- Amazon Web Services (infrastructure hosting, US regions)
- OpenAI / Anthropic (LLM processing, with data not used for training per our agreements)
- Datadog (monitoring, no PII transmitted)

The Processor shall notify the Controller at least 30 days before engaging a new sub-processor. The Controller may object to a new sub-processor within 14 days of notification.

## 5. Data Subject Rights

The Processor shall assist the Controller in responding to data subject requests (access, rectification, erasure, portability) within 10 business days. The Processor provides a self-serve data deletion API for programmatic erasure requests.

## 6. Data Retention and Deletion

Upon termination of the Agreement, the Processor shall delete all Customer Personal Data within 30 days. Customer may request an export of their data in JSON format prior to deletion. Backups are purged within 90 days of termination.

## 7. Breach Notification

The Processor shall notify the Controller of any Personal Data breach without undue delay and in any event within 48 hours of becoming aware of the breach. Notification shall include the nature of the breach, categories and approximate number of data subjects affected, and measures taken to mitigate.

## 8. International Transfers

For transfers outside the EEA, the Processor relies on Standard Contractual Clauses (Module 2: Controller to Processor) as adopted by the European Commission. A copy of the executed SCCs is available upon request.
