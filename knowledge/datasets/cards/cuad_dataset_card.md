# CUAD Dataset Card

## Dataset Information

**Name:** Contract Understanding Atticus Dataset (CUAD)
**Version:** v1
**Source:** https://huggingface.co/datasets/theatticusproject/cuad
**License:** CC-BY-4.0
**Created by:** The Atticus Project
**Task Type:** Legal Contract Analysis, Clause Classification, Entity Extraction

## Dataset Description

CUAD is a corpus of more than 13,000 labels across 510 commercial legal contracts designed to support NLP research in legal document analysis. It enables automated identification of 41 important clause categories that lawyers typically review during corporate transactions.

### Key Statistics

- **Total Samples:** 84,325 (train split)
- **Number of Contracts:** 510
- **Clause Categories:** 41
- **Text Length Range:** 0 to 6,970 characters
- **Format:** Parquet (5.45 MB compressed)
- **License:** CC-BY-4.0 (allows research and commercial use)

### Clause Categories

The dataset includes 41 clause categories divided into two types:

#### Binary Categories (33)
These require YES/NO answers about clause presence:
- Anti-Assignment
- Audit Rights
- Cap On Liability
- Change Of Control
- Competitive Restriction Exception
- Covenant Not To Sue
- Governing Law
- Insurance
- IP Ownership Assignment
- Joint IP Ownership
- License Grant
- Liquidated Damages
- Minimum Commitment
- Most Favored Nation
- Non-Compete
- Non-Disparagement
- Non-Solicit Of Customers
- Non-Solicit Of Employees
- Post-Termination Services
- Price Restrictions
- Renewal Term
- Revenue/Profit Sharing
- ROFR/ROFO/ROFN
- Source Code Escrow
- Termination For Convenience
- Third Party Beneficiary
- Uncapped Liability
- Unlimited/All-You-Can-Eat License
- Volume Restriction
- Warranty Duration

#### Entity Extraction Categories (8)
These require extracting specific entities, dates, or locations:
- Document Name
- Effective Date
- Expiration Date
- Notice Period To Terminate Renewal
- Parties (names and locations)
- Term Duration
- Agreement Value

### Data Format

#### Hugging Face Format
```json
{
  "text": "AMENDMENT TO SERVICES AGREEMENT This Amendment to Services Agreement...",
  "Anti-Assignment": true,
  "Audit Rights": false,
  ...
}
```

#### Available Formats
1. **Master CSV:** 83 columns x 511 rows with all annotations
2. **SQuAD 2.0 JSON:** For question-answering tasks
3. **Excel Files:** 28 files organized by clause category
4. **Raw Text:** 510 PDF and TXT files of full contracts

## Use Cases

### Primary Use Case: MAKER-Based Contract Review

Apply the MAKER framework (from paper arXiv:2511.09030) to achieve high-precision contract review:

1. **Decomposition:** Break each contract into 41 clause identification subtasks
2. **Error Correction:** Use multi-agent voting (k=3-5) for each clause
3. **Red-Flagging:** Discard uncertain or overly complex responses

Expected Performance:
- Accuracy: >95% F1 score per clause category
- Reliability: >90% zero-error contract reviews
- Cost: <$5 per contract with GPT-4.1-mini

### Additional Use Cases

1. **Legal Document Understanding:** Train models to understand contract structure
2. **Clause Extraction:** Extract specific clauses for downstream analysis
3. **Risk Assessment:** Identify high-risk clauses automatically
4. **Contract Comparison:** Compare clauses across multiple contracts
5. **Benchmarking:** Evaluate LLM performance on legal reasoning

## Dataset Structure

### Splits
- **train:** 84,325 samples (primary split)
- No explicit test/validation splits provided in standard distribution

### Features
- **text** (string): Contract clause text
- **[41 clause fields]** (various types): Annotations for each clause category

### Related Categories
Certain clause categories are grouped together for overlapping contexts:
- Non-compete related: Non-Compete, Non-Solicit Of Customers, Non-Solicit Of Employees
- IP related: IP Ownership Assignment, Joint IP Ownership, License Grant
- Termination related: Termination For Convenience, Notice Period, Post-Termination Services

## Citation

If you use this dataset, please cite:

```bibtex
@article{hendrycks2021cuad,
  title={CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review},
  author={Hendrycks, Dan and Burns, Collin and Chen, Anya and Ball, Spencer},
  journal={arXiv preprint arXiv:2103.06268},
  year={2021}
}
```

## Dataset Quality

### Strengths
- Expert-annotated by lawyers
- Covers real commercial contracts
- Comprehensive clause coverage (41 categories)
- Standardized annotation format
- Large enough for training and evaluation

### Limitations
- Single domain (commercial contracts)
- English language only
- May not cover all possible clause types
- Potential label noise (even with expert annotation)
- Imbalanced class distribution (some clauses rare)

## Ethical Considerations

### Privacy
- Contracts are from public sources or anonymized
- No personally identifiable information (PII) should be present
- Review for sensitive information before use in production

### Bias
- Dataset may reflect biases in commercial contracting practices
- Primarily US-based contracts
- May not generalize to other legal systems or contract types

### Intended Use
- Research and development of legal AI systems
- Training and benchmarking NLP models
- Educational purposes
- Commercial use allowed under CC-BY-4.0

### Out-of-Scope Use
- Should not replace human legal review for critical decisions
- Not suitable for automated contract generation without oversight
- Requires domain expertise for proper interpretation

## Related Resources

### Papers
- MAKER Framework: "Solving a Million-Step LLM Task with Zero Errors" (arXiv:2511.09030)
- Original CUAD Paper: Hendrycks et al., "CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review"

### Code
- HuggingFace Datasets: `load_dataset("theatticusproject/cuad")`
- This repo: `python -m pipelines.collect.collect_cuad`

### Related Datasets
- ContractNLI: Natural language inference for contracts
- LEDGAR: Legal provision classification
- MultiLegalPile: Large-scale legal text corpus

## Maintenance

**Last Updated:** 2025-12-22
**Status:** Active
**Contact:** The Atticus Project (via HuggingFace)
**Issues:** Report at HuggingFace dataset page

## Download Instructions

### Using HuggingFace Datasets
```python
from datasets import load_dataset

# Load full dataset
dataset = load_dataset("theatticusproject/cuad")

# Load specific split
train_data = load_dataset("theatticusproject/cuad", split="train")

# Load with streaming (for large datasets)
dataset = load_dataset("theatticusproject/cuad", streaming=True)
```

### Using This Repository
```bash
# Download 1000 samples for testing
python -m pipelines.collect.collect_cuad --split train --limit 1000

# Download full dataset
python -m pipelines.collect.collect_cuad --split train --limit -1

# Prepare for MAKER experiment
python -m pipelines.collect.collect_cuad --prepare-maker
```

### Direct Download
Visit https://huggingface.co/datasets/theatticusproject/cuad for additional download options.

## Version History

- **v1.0 (2021):** Initial release with 510 contracts and 41 clause categories
- No subsequent versions as of 2025-12-22

---

**Note:** This dataset card follows the template from [HuggingFace Dataset Cards](https://huggingface.co/docs/hub/datasets-cards).
