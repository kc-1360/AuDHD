import streamlit as st
import math

# --- UI Configuration ---
st.set_page_config(page_title="AuDHD Clinical Estimator", page_icon="🧠", layout="centered")

class FinalAuDHDEstimator:
    def __init__(self):
        # Base Subscales: (Threshold, Max Score, Clinical Weight Beta, Category)
        self.subscales = {
            'raads_social_relatedness': (31.0, 117.0, 1.8, 'ASD'),
            'raads_circumscribed_interests': (15.0, 42.0, 1.5, 'ASD'),
            'raads_language': (4.0, 21.0, 1.2, 'ASD'),
            'raads_sensorimotor': (16.0, 60.0, 1.4, 'ASD'),
            'aq_social_skill': (6.0, 10.0, 1.3, 'ASD'),
            'aq_attention_switching': (6.0, 10.0, 1.7, 'ASD'), 
            'aq_attention_to_detail': (6.0, 10.0, 1.1, 'ASD'),
            'aq_communication': (6.0, 10.0, 1.2, 'ASD'),
            'aq_imagination': (6.0, 10.0, 0.8, 'ASD'),
            'catq_compensation': (35.0, 63.0, 1.0, 'ASD'),
            'catq_masking': (35.0, 56.0, 1.3, 'ASD'),
            'catq_assimilation': (35.0, 56.0, 1.1, 'ASD'),
            
            'asrs_part_a': (14.0, 24.0, 2.0, 'ADHD'),
            'asrs_part_b': (6.0, 12.0, 1.2, 'ADHD'),
            'baars_inattention': (12.0, 27.0, 1.5, 'ADHD'),
            'baars_hyperactivity_impulsivity': (18.0, 27.0, 1.6, 'ADHD'),
            'baars_sct': (12.0, 27.0, 1.6, 'ADHD'),
            'wurs_25_total': (46.0, 100.0, 1.5, 'ADHD')
        }
        
        self.custom_questions = [
            "Routine Paradox: I desperately crave structure, but find myself unable to maintain a routine.",
            "Novelty vs Depth: My interests are incredibly deep, but I rotate through them rapidly.",
            "Sensory Chaos: I need perfect physical organization to function, but I constantly make messes.",
            "The Stimulant Paradox: Stimulants calm my thoughts, but worsen my sensory sensitivities.",
            "Masking Exhaustion: I can socialize highly effectively, but it causes severe delayed burnout."
        ]

        self.validity_questions = [
            "When I lose focus on a task, I frequently forget my own name or what year it is for several hours.",
            "I have never, not even once in my entire life, successfully completed a single task.",
            "I physically lose my vision (go blind) for a few minutes when I hear a sound that is too loud."
        ]
        
        # Independent Intercepts for mathematical isolation
        self.intercept_asd = -15.4
        self.intercept_adhd = -9.4
        self.interaction_weight = 0.8  # Slightly boosted to account for the new strict bottleneck
        
        # Likert Mapping
        self.likert_options = {
            "0 - Never / Strongly Disagree": 0,
            "1 - Rarely / Disagree": 1,
            "2 - Sometimes / Neutral": 2,
            "3 - Often / Agree": 3,
            "4 - Always / Strongly Agree": 4
        }

    def run_ui(self):
        st.title("🧠 Advanced Clinical Estimator")
        st.markdown("This tool calculates the independent mathematical probabilities for ASD, ADHD, and the combined AuDHD phenotype.")
        st.markdown("#### Please take the following quizzes before you start:")
        st.markdown("https://autismtestonline.org/test/raads-r")
        st.markdown("https://autismtestonline.org/test/aq-50")
        st.markdown("https://autismtestonline.org/test/cat-q")
        st.markdown("https://autismtestonline.org/test/cat-q")       
        st.markdown("For ASRS Pt A: https://adhdquiz.com.au/asrs/") 
        st.markdown("For ASRS Pt B: https://psychology-tools.com/test/adult-adhd-self-report-scale")
        st.markdown("https://www.relationalpsych.group/quizzes/adhd-quiz")
        st.markdown("https://adhdquiz.com.au/wurs/")
        
        st.divider()

        # --- STEP 1: Clinical Subscales ---
        st.header("Step 1: Clinical Subscales")
        st.markdown("Enter your raw scores. Blind validation protocols are active in the background.")
        scores = {}
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Autism Scales (ASD)")
            for subscale, data in self.subscales.items():
                if data[3] == 'ASD':
                    name = subscale.replace('_', ' ').title().replace('Aq', 'AQ').replace('Catq', 'CAT-Q').replace('Raads', 'RAADS')
                    scores[subscale] = st.number_input(f"{name}", min_value=0, max_value=int(data[1]), value=0, step=1)

        with col2:
            st.subheader("ADHD Scales")
            for subscale, data in self.subscales.items():
                if data[3] == 'ADHD':
                    name = subscale.replace('_', ' ').title().replace('Asrs', 'ASRS').replace('Baars', 'BAARS').replace('Wurs', 'WURS')
                    scores[subscale] = st.number_input(f"{name}", min_value=0, max_value=int(data[1]), value=0, step=1)

        st.divider()

        # --- STEP 2: Custom Phenotype (Radio Buttons) ---
        st.header("Step 2: AuDHD Internal Friction Scale")
        st.markdown("To prevent anchoring bias, no default answers are selected. You must manually select an option for each.")
        
        custom_score = 0
        all_custom_answered = True
        for i, q in enumerate(self.custom_questions):
            ans = st.radio(q, list(self.likert_options.keys()), index=None, horizontal=True, key=f"custom_{i}")
            if ans is not None:
                custom_score += self.likert_options[ans]
            else:
                all_custom_answered = False

        st.divider()

        # --- STEP 3: Validity Check (Radio Buttons) ---
        st.header("Step 3: Baseline Verification")
        validity_score = 0
        all_valid_answered = True
        for i, q in enumerate(self.validity_questions):
            ans = st.radio(q, list(self.likert_options.keys()), index=None, horizontal=True, key=f"valid_{i}")
            if ans is not None:
                validity_score += self.likert_options[ans]
            else:
                all_valid_answered = False

        st.divider()

        # --- CALCULATION & RESULTS ---
        if st.button("Calculate My Profile", type="primary"):
            if not (all_custom_answered and all_valid_answered):
                st.warning("⚠️ Please select an answer for all multiple-choice questions before calculating.")
                st.stop()
                
            # Data Validation Trigger
            if validity_score > 4:
                st.error("🚨 DATA INVALIDATION PROTOCOL TRIGGERED")
                st.write("The system detected responses on the Infrequency Scale that are statistically highly improbable. Results cannot be calculated due to suspected over-reporting or data tampering.")
                st.stop()

            # Execute Math
            self.display_results(scores, custom_score)

    def display_results(self, scores, custom_score):
        z_asd = self.intercept_asd
        z_adhd = self.intercept_adhd
        
        total_user_score = 0
        total_max_score = 0
        
        asd_composite = 0
        asd_max_composite = 0
        adhd_composite = 0
        adhd_max_composite = 0
        
        for subscale, score in scores.items():
            threshold, max_score, weight, category = self.subscales[subscale]
            normalized_score = score / threshold
            
            total_user_score += score
            total_max_score += max_score
            
            if category == 'ASD':
                z_asd += normalized_score * weight
                asd_composite += normalized_score
                asd_max_composite += (max_score / threshold)
            elif category == 'ADHD':
                z_adhd += normalized_score * weight
                adhd_composite += normalized_score
                adhd_max_composite += (max_score / threshold)

        # Apply Interaction Term
        interaction_effect = (asd_composite / 12.0) * (adhd_composite / 6.0) * self.interaction_weight
        
        # COMORBIDITY BOTTLENECK: The "AND" Gate
        # By taking the minimum of the two independent log-odds, we ensure that an 
        # extremely high ASD score cannot falsely artificially inflate the comorbidity score 
        # if the ADHD score is low (and vice versa).
        z_audhd_base = min(z_asd, z_adhd)

        # The custom AuDHD friction traits and the statistical interaction effect 
        # are then added to this bottlenecked baseline.
        z_audhd = z_audhd_base + ((custom_score / 12.0) * 3.0) + interaction_effect

        # Final Sigmoid Conversions
        prob_asd = 1 / (1 + math.exp(-z_asd))
        prob_adhd = 1 / (1 + math.exp(-z_adhd))
        prob_audhd = 1 / (1 + math.exp(-z_audhd))
        
        severity_ratio = total_user_score / total_max_score

        # Display Metrics
        st.header("📊 Independent Probabilities")
        
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Probability of ASD", f"{prob_asd * 100:.2f}%")
        col_b.metric("Probability of ADHD", f"{prob_adhd * 100:.2f}%")
        col_c.metric("Probability of AuDHD", f"{prob_audhd * 100:.2f}%")
        
        st.progress(prob_asd, text="Isolated Autism Probability")
        st.progress(prob_adhd, text="Isolated ADHD Probability")
        st.progress(prob_audhd, text="Compounded Comorbidity Probability")
        
        st.divider()
        st.subheader("Dominance & Interaction Analysis")
        st.write(f"**Total Symptom Burden:** {severity_ratio * 100:.2f}% of maximum traits across all tests.")
        
        asd_burden = asd_composite / asd_max_composite if asd_max_composite > 0 else 0
        adhd_burden = adhd_composite / adhd_max_composite if adhd_max_composite > 0 else 0

        # DOMINANCE LOGIC
        if asd_burden > adhd_burden + 0.15:
            st.write("📈 **Autism (ASD) Dominant.** Your data suggests the structured, detail-oriented, and sensory-specific traits significantly outweigh the executive chaos traits.")
        elif adhd_burden > asd_burden + 0.15:
            st.write("📈 **ADHD Dominant.** Your data suggests executive dysfunction, hyperkinesia, and novelty-seeking significantly outweigh rigid, systemizing traits.")
        else:
            st.write("⚖️ **Co-Dominant / Balanced.** Neither neurotype significantly outpaces the other. Your profile is heavily balanced, which typically causes the highest internal friction.")

        # INTERACTION LOGIC
        if prob_audhd > 0.70:
            st.success("High Interaction Detected: Your profile shows a strong statistical clash between high-structure needs and high-chaos traits. This friction is the hallmark of the AuDHD phenotype.")
        elif prob_audhd > 0.40:
            st.info("Moderate Interaction: Traits of both are present, but the paradoxical comorbidity clash is less severe.")
        else:
            st.warning("Low Interaction: The data suggests your traits fall predominantly along a single axis, lacking the compounding friction of a comorbidity.")

if __name__ == "__main__":
    app = FinalAuDHDEstimator()
    app.run_ui()
