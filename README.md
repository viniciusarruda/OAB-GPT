# OAB-GPT

Ask any OAB exam question and get the correct answer.
[Demo](https://oabgpt.streamlit.app/)

## Installation

Developed using `python 3.10` on windows.

```bash
pip install -r requirements.txt
```

## Usage

### To run the app

```bash
streamlit run app.py
```

### To ingest PDF files

First, rename the folder in `ingestor.py` to not overwrite the current ingested files.
Place the PDFs into the `data/pdf` directory, then:

```bash
python ingestor.py
```

For the OAB app, the following PDFs were used:

[Vade Mecum DEPEN](https://dhg1h5j42swfq.cloudfront.net/2020/05/12153746/VADE-ME%CC%81CUM_DEPEN.pdf)
[Vade Mecum Digital Saraiva 2022](https://livrogratuitosja.com/wp-content/uploads/2023/01/VADE-MECUM-DIGITAL-SARAIVA-2022.pdf)
