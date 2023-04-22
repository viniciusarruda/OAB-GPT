import os
import streamlit as st
from langchain.chains import LLMChain
from langchain.prompts.prompt import PromptTemplate
from langchain.llms import OpenAI

import ingestor

# from pprint import pprint

st.set_page_config(page_title="OAB-GPT")


# TODO: load a OAB exam. Problem: Correctly format the PDF
# def read_and_save_file():
#     if st.session_state["file_uploader"]:
#         file_name = st.session_state["file_uploader"].name
#         with tempfile.NamedTemporaryFile(delete=False) as tf:
#             tf.write(st.session_state["file_uploader"].getbuffer())
#             file_path = tf.name

#         with st.session_state["file_uploader_spinner"], st.spinner(f"Ingesting {file_name}"):
#             loader = PyPDFLoader(file_path)
#             documents = loader.load()
#         os.remove(file_path)

#         for doc in documents:
#             st.text(doc.page_content)
#             st.write(doc.metadata)
#             st.divider()
#         st.divider()


@st.cache_resource
def get_db():
    return ingestor.get_db()


def is_openai_api_key_set() -> bool:
    return len(st.session_state["OPENAI_API_KEY"]) > 0


@st.cache_resource
def create_chain():
    template = """Dado o seguinte contexto, a questão, e as opções de resposta, analise cada opção se está correta ou errada e justifique. Somente uma opção está correta.

Contexto:
- {context}
    
Questão: 
- {question}

Opções:
- {options}

Justificativa:"""
    prompt = PromptTemplate(template=template, input_variables=["context", "question", "options"])
    return LLMChain(prompt=prompt, llm=OpenAI(temperature=0, max_tokens=512), verbose=False)


def build_context(query: str) -> list[str]:
    docs = st.session_state["db"].similarity_search(query)
    # pprint(docs)
    return "\n".join([d.page_content for d in docs])


def main():
    options = ["A", "B", "C", "D"]

    with st.sidebar:
        st.title(":bookmark_tabs: OAB-GPT")

        st.header("Como funciona?")
        st.subheader('1. Insira a chave da API no campo "OpenAI API Key".')
        st.markdown(
            "Para acessar sua chave, acesse [aqui](https://platform.openai.com/account/api-keys). Caso tiver dúvidas, assista este [tutorial](https://www.youtube.com/watch?v=Kfuh4v_hqnw&ab_channel=GianCampos) de 1 minuto."
        )

        st.subheader('2. Insira a questão e as opções de respostas de uma prova da OAB, e em seguida clique "Responder".')

        st.markdown("Para acessar as provas da OAB, acesse [aqui](https://oab.fgv.br/).")

        st.divider()
        st.markdown(
            "Feito por Vinicius Arruda [[Github]](https://github.com/viniciusarruda) [[LinkedIn]](https://www.linkedin.com/in/viniciusarruda/)"
        )
        st.markdown("Código fonte: [Github](https://github.com/viniciusarruda/OAB-GPT)")
        st.markdown(
            """
            <a href="https://www.buymeacoffee.com/viniciusarruda" target="_blank">
            <img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174">
            </a>
            """,
            unsafe_allow_html=True,
        )

    if len(st.session_state) == 0:
        st.session_state["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "")
        if is_openai_api_key_set():
            st.session_state["llm_chain"] = create_chain()
            with st.spinner("Carregando informações..."):
                st.session_state["db"] = get_db()
        else:
            st.session_state["llm_chain"] = None
            st.session_state["db"] = None

    st.header("OAB-GPT")

    # If change api_key
    if st.text_input("OpenAI API Key", value=st.session_state["OPENAI_API_KEY"], key="input_OPENAI_API_KEY", type="password"):
        if (
            len(st.session_state["input_OPENAI_API_KEY"]) > 0
            and st.session_state["input_OPENAI_API_KEY"] != st.session_state["OPENAI_API_KEY"]
        ):
            st.session_state["OPENAI_API_KEY"] = st.session_state["input_OPENAI_API_KEY"]
            if st.session_state["llm_chain"] is not None:
                st.warning("Please, upload the files again.")
            st.session_state["question"] = ""
            # TODO

    # st.subheader("Carregue uma prova da OAB")
    # st.file_uploader(
    #     "Upload document",
    #     type=["pdf"],
    #     key="file_uploader",
    #     on_change=read_and_save_file,
    #     label_visibility="collapsed",
    #     disabled=not is_openai_api_key_set(),
    # )
    # st.session_state["file_uploader_spinner"] = st.empty()

    st.text_area("Questão", key="question", disabled=not is_openai_api_key_set())

    for option in options:
        st.text_area(f"{option})", key=option, disabled=not is_openai_api_key_set())
    placeholder = st.empty()

    is_fields_filled = len(st.session_state["question"]) > 0 and all([len(st.session_state[option]) > 0 for option in options])
    if st.button("Responder", disabled=not is_fields_filled):
        with st.spinner("Pensando..."):
            prediction = st.session_state["llm_chain"].predict(
                context=build_context(st.session_state["question"]),
                question=st.session_state["question"],
                options="\n- ".join([f"{option}) " + st.session_state[option] for option in options]),
            )
            placeholder.markdown(str(prediction))


if __name__ == "__main__":
    main()
