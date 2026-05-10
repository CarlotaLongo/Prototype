import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="NLP Restaurant Review Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)



POSITIVE_WORDS = {
    "amazing", "excellent", "fantastic", "great", "good", "delicious", "wonderful",
    "loved", "love", "best", "awesome", "perfect", "tasty", "fresh", "friendly",
    "attentive", "cozy", "clean", "beautiful", "nice", "enjoyed", "superb",
    "outstanding", "pleasant", "helpful", "quick", "fast", "polite", "warm",
    "charming", "recommended", "recommend", "impressive", "happy", "satisfied",
    "reasonable", "affordable", "worth", "value"
}

NEGATIVE_WORDS = {
    "terrible", "awful", "bad", "worst", "horrible", "disgusting", "rude",
    "slow", "cold", "dirty", "disappointing", "disappointed", "mediocre",
    "overpriced", "expensive", "poor", "bland", "stale", "unfriendly",
    "unhelpful", "noisy", "loud", "cramped", "dark", "waited", "wait",
    "wrong", "mistake", "ignored", "filthy", "gross", "undercooked",
    "overcooked", "soggy", "greasy", "tasteless", "inattentive", "unprofessional"
}

ASPECT_KEYWORDS = {
    "Food": {
        "food", "dish", "meal", "taste", "flavor", "flavour", "menu", "portion",
        "ingredients", "cooked", "chef", "cuisine", "burger", "pizza", "pasta",
        "steak", "dessert", "appetizer", "salad", "soup", "breakfast", "lunch",
        "dinner", "delicious", "tasty", "fresh", "bland", "overcooked", "undercooked",
        "soggy", "greasy", "tasteless", "spicy", "sweet", "salty"
    },
    "Service": {
        "service", "staff", "waiter", "waitress", "server", "manager", "host",
        "hostess", "rude", "friendly", "attentive", "slow", "fast", "quick",
        "waited", "wait", "ignored", "helpful", "polite", "unprofessional",
        "efficient", "inattentive", "bartender", "team"
    },
    "Ambiance": {
        "ambiance", "ambience", "atmosphere", "decor", "decoration", "interior",
        "music", "lighting", "noise", "noisy", "loud", "quiet", "cozy", "cramped",
        "spacious", "clean", "dirty", "filthy", "vibe", "setting", "view",
        "comfortable", "uncomfortable", "romantic", "beautiful", "ugly"
    },
    "Price": {
        "price", "prices", "priced", "expensive", "cheap", "affordable", "overpriced",
        "value", "worth", "cost", "bill", "charge", "reasonable", "pricey",
        "budget", "money", "tip", "pay", "paid"
    }
}

def analyze_review(text: str):
    words = text.lower().split()
    cleaned = set(w.strip(".,!?;:\"'()") for w in words)

    pos_hits = cleaned & POSITIVE_WORDS
    neg_hits = cleaned & NEGATIVE_WORDS

    pos_count = len(pos_hits)
    neg_count = len(neg_hits)

    if pos_count > neg_count:
        sentiment, color = "Positive", "#4CAF50"
    elif neg_count > pos_count:
        sentiment, color = "Negative", "#F44336"
    else:
        sentiment, color = "Neutral", "#FFC107"

    import re
    sentences = re.split(r"[.!?,;]", text.lower())

    detected_aspects = {}
    for aspect, keywords in ASPECT_KEYWORDS.items():
        matched = cleaned & keywords
        if not matched:
            continue
        # Collect words from sentences that mention this aspect
        context_words = set()
        for sentence in sentences:
            s_words = set(w.strip(".,!?;:()'\" ") for w in sentence.split())
            if s_words & keywords:
                context_words |= s_words
        p = len(context_words & POSITIVE_WORDS)
        n = len(context_words & NEGATIVE_WORDS)
        if p > n:
            asp_sentiment, asp_scolor = "Positive", "#4CAF50"
        elif n > p:
            asp_sentiment, asp_scolor = "Negative", "#F44336"
        else:
            asp_sentiment, asp_scolor = "Neutral", "#FFC107"
        detected_aspects[aspect] = {
            "keywords": list(matched),
            "sentiment": asp_sentiment,
            "scolor": asp_scolor,
        }

    return sentiment, color, pos_hits, neg_hits, detected_aspects


def render_review_analyzer():
    st.markdown("Paste any restaurant review below to instantly detect its **overall sentiment** and **mentioned aspects** using keyword-based rules.")

    review_text = st.text_area(
        label="Review Text",
        height=140,
        label_visibility="collapsed"
    )

    analyze_clicked = st.button("Analyze Review", type="primary")

    if analyze_clicked:
        if not review_text.strip():
            st.warning("Please paste a review before clicking Analyze.")
            return

        sentiment, color, pos_hits, neg_hits, aspects = analyze_review(review_text)

        st.markdown("---")

        st.subheader("Overall Sentiment")
        st.markdown(
            f"<div style='display:inline-block; padding: 10px 24px; border-radius: 8px; "
            f"background-color:{color}22; border: 2px solid {color}; "
            f"font-size: 1.3em; font-weight: bold; color:{color};'>"
            f"{sentiment}</div>",
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)
        col_pos, col_neg = st.columns(2)
        with col_pos:
            if pos_hits:
                st.markdown(
                    f"<span style='color:#4CAF50; font-weight:bold;'>Positive signals:</span> "
                    f"{', '.join(sorted(pos_hits))}",
                    unsafe_allow_html=True
                )
        with col_neg:
            if neg_hits:
                st.markdown(
                    f"<span style='color:#F44336; font-weight:bold;'>Negative signals:</span> "
                    f"{', '.join(sorted(neg_hits))}",
                    unsafe_allow_html=True
                )

        st.markdown("---")

        st.subheader("Detected Aspects")

        if not aspects:
            st.info("No specific aspects detected. Try a more descriptive review.")
        else:
            aspect_colors = {
                "Food":     "#FF9800",
                "Service":  "#2196F3",
                "Ambiance": "#9C27B0",
                "Price":    "#00BCD4",
            }
            cols = st.columns(len(aspects))
            for col, (aspect, data) in zip(cols, aspects.items()):
                acolor = aspect_colors.get(aspect, "#888888")
                asp_sentiment = data["sentiment"]
                asp_scolor = data["scolor"]
                kws = ", ".join(sorted(data["keywords"]))
                with col:
                    st.markdown(
                        f"<div style='border-radius:8px; padding:14px; "
                        f"border: 2px solid {acolor}; background:{acolor}15;'>"
                        f"<div style='font-size:1.1em; font-weight:bold; color:{acolor};'>{aspect}</div>"
                        f"<div style='margin-top:8px; display:inline-block; padding:3px 12px; "
                        f"border-radius:5px; background:{asp_scolor}22; border:1px solid {asp_scolor}; "
                        f"font-size:0.85em; font-weight:bold; color:{asp_scolor};'>{asp_sentiment}</div>"
                        f"<div style='margin-top:8px; font-size:0.82em; color:#aaa;'>"
                        f"Keywords: {kws}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )


def render_model_comparison():
    st.header("RQ1: Model Comparison")

    models = [
        "SVM (TF-IDF)",
        "DistilBERT (no FT)",
        "DistilBERT (FT)",
        "RoBERTa (no FT)",
        "RoBERTa (FT)"
    ]

    macro_f1 = [0.5571, 0.5700, 0.6400, 0.6980, 0.6910]
    micro_f1 = [0.6708, 0.6510, 0.7300, 0.7670, 0.7920]

    colors = {
        "SVM (TF-IDF)": "#B0BEC5",
        "DistilBERT (no FT)": "#CFD8DC",
        "DistilBERT (FT)": "#90A4AE",
        "RoBERTa (no FT)": "#64B5F6",
        "RoBERTa (FT)": "#B39DDB",
    }

    common_layout = dict(
        yaxis=dict(
            range=[0, 0.85],
            tick0=0,
            dtick=0.2,
            fixedrange=True
        ),
        template="plotly_dark",
        autosize=False,
        height=430,
        margin=dict(t=60, b=60, l=70, r=30),
    )

    col1, col2 = st.columns(2)

    with col1:
        fig_macro = go.Figure()

        for model, value in zip(models, macro_f1):
            fig_macro.add_trace(go.Bar(
                x=[model],
                y=[value],
                marker_color=colors[model],
                text=[f"{value:.3f}"],
                textposition="outside",
                showlegend=False
            ))

        fig_macro.update_layout(
            title="Macro F1 Score",
            yaxis_title="Macro F1",
            **common_layout
        )

        st.plotly_chart(fig_macro, use_container_width=True)

    with col2:
        fig_micro = go.Figure()

        for model, value in zip(models, micro_f1):
            fig_micro.add_trace(go.Bar(
                x=[model],
                y=[value],
                marker_color=colors[model],
                text=[f"{value:.3f}"],
                textposition="outside",
                showlegend=False
            ))

        fig_micro.update_layout(
            title="Micro F1 Score",
            yaxis_title="Micro F1",
            **common_layout
        )

        st.plotly_chart(fig_micro, use_container_width=True)



    st.info(
        "RoBERTa achieved the best overall performance. "
        "Fine-tuning only slightly improves Micro F1, while Macro F1 remains almost unchanged. "
    )
def render_length_bias():
    st.header("RQ2: Review Length Bias")

    lengths = ["Short", "Medium", "Long"]
    svm_scores = [0.942, 0.924, 0.892]
    bert_scores = [0.965, 0.930, 0.933]

    fig = go.Figure()


    fig.add_trace(go.Bar(
        x=lengths,
        y=svm_scores,
        name="SVM (TF-IDF)",
        marker_color="#C7C7C7",
        width=0.25,
        text=[f"{v:.3f}" for v in svm_scores],
        textposition="outside"
    ))


    fig.add_trace(go.Bar(
        x=lengths,
        y=bert_scores,
        name="DistilBERT",
        marker_color="#A7C7E7",
        width=0.25,
        text=[f"{v:.3f}" for v in bert_scores],
        textposition="outside"
    ))

    fig.update_layout(
        title="Aspect Detection Performance by Review Length",
        xaxis_title="Review Length Category",
        yaxis_title="Micro-F1 Score",
        yaxis=dict(range=[0.85, 1.0]),
        barmode="group",
        bargap=0.4,
        bargroupgap=0.2,
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(fig, use_container_width=True)
def render_sentiment_alignment():
    st.header("RQ3: Sentiment Alignment")
    st.markdown(
    """
    <div style='text-align: center; font-size: 24px; margin-top: 10px; margin-bottom: 40px;'>
        <b>Spearman Rank Correlation: ρ = 0.720</b>
    </div>
    """,
    unsafe_allow_html=True
)
    st.markdown(
        "<h4 style='text-align: center;'>True Sentiment Label vs. Predicted Sentiment Label</h4>",
        unsafe_allow_html=True
    )

    sentiment_matrix = [
        [6884, 807, 603],
        [1455, 962, 2171],
        [719, 1116, 25279]
    ]

    fig1 = go.Figure(data=go.Heatmap(
        z=sentiment_matrix,
        x=["negative", "neutral", "positive"],
        y=["negative", "neutral", "positive"],
        colorscale="Blues",
        text=sentiment_matrix,
        texttemplate="%{text}",
        textfont={"size": 15},
        colorbar=dict(title="Count")
    ))

    fig1.update_layout(
        xaxis_title="Predicted label",
        yaxis_title="True label",
        yaxis=dict(autorange="reversed"),
        template="plotly_white"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        "<h4 style='text-align: center;'>Real Star Rating vs. Predicted Sentiment</h4>",
        unsafe_allow_html=True
    )

    rating_matrix = [
        [4310, 291, 181],
        [2574, 516, 422],
        [1455, 962, 2171],
        [494, 717, 8391],
        [225, 399, 16888]
    ]

    fig2 = go.Figure(data=go.Heatmap(
        z=rating_matrix,
        x=["negative", "neutral", "positive"],
        y=["1 star", "2 star", "3 star", "4 star", "5 star"],
        colorscale="YlOrRd",
        text=rating_matrix,
        texttemplate="%{text:,}",
        textfont={"size": 15},
        colorbar=dict(title="Number of reviews")
    ))

    fig2.update_layout(
        xaxis_title="Predicted Sentiment",
        yaxis_title="Real Star Rating (Yelp)",
        yaxis=dict(autorange="reversed"),
        template="plotly_white"
    )

    st.plotly_chart(fig2, use_container_width=True)

def render_scientific_eval():
    col1, col2 = st.columns([1, 4])
    with col1:
        st.subheader("Menu")
        view_selection = st.radio(
            "Select Evaluation View:",
            options=["Model Comparison (RQ1)", "Review Length Bias (RQ2)", "Sentiment Alignment (RQ3)"]
        )
    with col2:
        if view_selection == "Model Comparison (RQ1)":
            render_model_comparison()
        elif view_selection == "Review Length Bias (RQ2)":
            render_length_bias()
        else:
            render_sentiment_alignment()


def render_managerial_dashboard():
    restaurant_list = ["Restaurant A", "Restaurant B", "Restaurant C", "Restaurant D", "Restaurant E"]
    selected_restaurant = st.selectbox("Select Restaurant to Analyze:", restaurant_list)

    st.markdown("---")

    col_food, col_service, col_ambiance, col_price = st.columns(4)

    with col_food:
        st.subheader("Food")
        st.progress(0.66, text="[X]% Positive Sentiment")
        with st.expander("View Evidence ([X] mentions)"):
            st.markdown("""
            "[Extracted review quote highlighting the specific aspect will be displayed here, with key phrases in **bold**.]"
            <br><span style='color:gray; font-size: 0.8em;'>Review ID: #[X] | Date: [Date] | Rating: [X] Stars | [Flag Status]</span>

            "[Another extracted review quote...]"
            <br><span style='color:gray; font-size: 0.8em;'>Review ID: #[X] | Date: [Date] | Rating: [X] Stars | [Flag Status]</span>
            """, unsafe_allow_html=True)

    with col_service:
        st.subheader("Service")
        st.progress(0.33, text="[X]% Positive Sentiment")
        with st.expander("View Evidence ([X] mentions)"):
            st.markdown("""
            "[Extracted review quote highlighting the specific aspect will be displayed here, with key phrases in **bold**.]"
            <br><span style='color:gray; font-size: 0.8em;'>Review ID: #[X] | Date: [Date] | Rating: [X] Stars | [Flag Status]</span>

            "[Another extracted review quote...]"
            <br><span style='color:gray; font-size: 0.8em;'>Review ID: #[X] | Date: [Date] | Rating: [X] Stars | [Flag Status]</span>
            """, unsafe_allow_html=True)

    with col_ambiance:
        st.subheader("Ambiance")
        st.progress(0.81, text="[X]% Positive Sentiment")
        with st.expander("View Evidence ([X] mentions)"):
            st.markdown("""
            "[Extracted review quote highlighting the specific aspect will be displayed here, with key phrases in **bold**.]"
            <br><span style='color:gray; font-size: 0.8em;'>Review ID: #[X] | Date: [Date] | Rating: [X] Stars | [Flag Status]</span>

            "[Another extracted review quote...]"
            <br><span style='color:gray; font-size: 0.8em;'>Review ID: #[X] | Date: [Date] | Rating: [X] Stars | [Flag Status]</span>
            """, unsafe_allow_html=True)

    with col_price:
        st.subheader("Price")
        st.progress(0.50, text="[X]% Positive Sentiment")
        with st.expander("View Evidence ([X] mentions)"):
            st.markdown("""
            "[Extracted review quote highlighting the specific aspect will be displayed here, with key phrases in **bold**.]"
            <br><span style='color:gray; font-size: 0.8em;'>Review ID: #[X] | Date: [Date] | Rating: [X] Stars | [Flag Status]</span>

            "[Another extracted review quote...]"
            <br><span style='color:gray; font-size: 0.8em;'>Review ID: #[X] | Date: [Date] | Rating: [X] Stars | [Flag Status]</span>
            """, unsafe_allow_html=True)



def main():
    st.title("NLP Restaurant Review Analysis")

    st.sidebar.markdown("### Project info")
    st.sidebar.markdown("**Models:** SVM (TF-IDF), DistilBERT, RoBERTa")

    tab1, tab2, tab3 = st.tabs(["Scientific Evaluation", "Managerial Dashboard", "Analyze a Review"])

    with tab1:
        render_scientific_eval()
    with tab2:
        render_managerial_dashboard()
    with tab3:
        render_review_analyzer()

if __name__ == "__main__":
    main()

