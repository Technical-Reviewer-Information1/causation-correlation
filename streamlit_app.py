import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="因果関係と疑似相関分析",
    page_icon="📊",
    layout="wide"
)

def calculate_correlation_metrics(x, y):
    """Calculate various correlation metrics"""
    # Pearson correlation
    pearson_r, pearson_p = stats.pearsonr(x, y)
    
    # Spearman correlation
    spearman_r, spearman_p = stats.spearmanr(x, y)
    
    # R-squared from linear regression
    lr = LinearRegression()
    X_reshaped = x.values.reshape(-1, 1)
    lr.fit(X_reshaped, y)
    r_squared = lr.score(X_reshaped, y)
    
    return {
        'pearson_r': pearson_r,
        'pearson_p': pearson_p,
        'spearman_r': spearman_r,
        'spearman_p': spearman_p,
        'r_squared': r_squared
    }

def create_scatter_plot(df, x_col, y_col, title_suffix=""):
    """Create a scatter plot with regression line"""
    fig = px.scatter(
        df, x=x_col, y=y_col,
        trendline="ols",
        title=f"散布図: {x_col} vs {y_col} {title_suffix}",
        labels={x_col: x_col, y_col: y_col}
    )
    
    # Calculate correlation metrics
    metrics = calculate_correlation_metrics(df[x_col], df[y_col])
    
    # Add annotation with correlation info
    fig.add_annotation(
        x=0.02, y=0.98,
        xref="paper", yref="paper",
        text=f"Pearson r = {metrics['pearson_r']:.3f}<br>" +
             f"R² = {metrics['r_squared']:.3f}<br>" +
             f"p-value = {metrics['pearson_p']:.3e}",
        showarrow=False,
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="black",
        borderwidth=1
    )
    
    return fig, metrics

def create_correlation_heatmap(df, selected_cols):
    """Create a correlation heatmap"""
    corr_matrix = df[selected_cols].corr()
    
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        title="相関行列ヒートマップ",
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1
    )
    
    return fig

def analyze_causation_indicators(df, x_col, y_col):
    """Analyze potential indicators of causation vs correlation"""
    
    indicators = {}
    
    # 1. Temporal precedence (if time-related variables exist)
    time_cols = [col for col in df.columns if any(keyword in col.lower() 
                for keyword in ['time', 'date', 'year', 'month', 'day', 'age'])]
    
    # 2. Strength of correlation
    metrics = calculate_correlation_metrics(df[x_col], df[y_col])
    correlation_strength = abs(metrics['pearson_r'])
    
    if correlation_strength > 0.7:
        strength_assessment = "強い相関"
    elif correlation_strength > 0.5:
        strength_assessment = "中程度の相関"
    elif correlation_strength > 0.3:
        strength_assessment = "弱い相関"
    else:
        strength_assessment = "非常に弱い相関"
    
    indicators['correlation_strength'] = {
        'value': correlation_strength,
        'assessment': strength_assessment
    }
    
    # 3. Linearity check
    residuals = []
    if len(df) > 10:
        lr = LinearRegression()
        X_reshaped = df[x_col].values.reshape(-1, 1)
        y_pred = lr.fit(X_reshaped, df[y_col]).predict(X_reshaped)
        residuals = df[y_col] - y_pred
        
        # Durbin-Watson test for autocorrelation
        try:
            from scipy.stats import jarque_bera
            jb_stat, jb_p = jarque_bera(residuals)
            indicators['residual_normality'] = {
                'jb_statistic': jb_stat,
                'jb_p_value': jb_p,
                'assessment': "正規分布に従う" if jb_p > 0.05 else "正規分布に従わない"
            }
        except:
            indicators['residual_normality'] = {'assessment': "計算できませんでした"}
    
    # 4. Outlier detection
    if len(df) > 10:
        z_scores_x = np.abs(stats.zscore(df[x_col]))
        z_scores_y = np.abs(stats.zscore(df[y_col]))
        outliers_x = np.sum(z_scores_x > 3)
        outliers_y = np.sum(z_scores_y > 3)
        
        indicators['outliers'] = {
            'x_outliers': outliers_x,
            'y_outliers': outliers_y,
            'total_outliers': outliers_x + outliers_y
        }
    
    return indicators

def display_causation_guidance(x_col, y_col, indicators):
    """Display guidance for interpreting causation vs correlation"""
    
    st.subheader("🔍 因果関係 vs 相関関係の判断指針")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ 因果関係を示唆する要因")
        st.markdown("""
        - **時間的前後関係**: 原因が結果より時間的に先行する
        - **理論的根拠**: 科学的・論理的な説明がある
        - **統制実験**: 他の要因を統制した実験結果
        - **用量反応関係**: 原因の強度と結果の強度が比例
        - **一貫性**: 異なる研究・集団で再現される
        """)
        
    with col2:
        st.markdown("### ⚠️ 疑似相関の可能性")
        st.markdown("""
        - **第三の変数**: 両方に影響する隠れた要因の存在
        - **偶然の一致**: 統計的な偶然による見かけの関係
        - **サンプリングバイアス**: 特定の集団に偏ったデータ
        - **測定誤差**: データ収集・測定の問題
        - **非線形関係**: 単純な線形関係の仮定が不適切
        """)
    
    # Current analysis summary
    st.markdown("### 📊 現在の分析結果")
    
    strength = indicators.get('correlation_strength', {})
    if strength:
        st.metric(
            "相関の強さ",
            f"{strength['value']:.3f}",
            delta=strength['assessment']
        )
    
    # Warnings and recommendations
    st.markdown("### 💡 分析のポイント")
    
    warnings_list = []
    recommendations = []
    
    if strength.get('value', 0) > 0.8:
        warnings_list.append("非常に強い相関が検出されました。測定誤差や第三の変数の影響を検討してください。")
    
    if 'outliers' in indicators:
        total_outliers = indicators['outliers']['total_outliers']
        if total_outliers > len(st.session_state.df) * 0.05:  # 5%以上が外れ値
            warnings_list.append(f"外れ値が{total_outliers}個検出されました。これらが結果に与える影響を確認してください。")
    
    recommendations.extend([
        "複数の角度からデータを分析する",
        "他の関連変数も考慮に入れる", 
        "時系列データがある場合は時間的関係を確認する",
        "専門知識を活用して理論的妥当性を検討する"
    ])
    
    if warnings_list:
        st.warning("⚠️ 注意点:")
        for warning in warnings_list:
            st.write(f"• {warning}")
    
    st.info("💡 推奨事項:")
    for rec in recommendations:
        st.write(f"• {rec}")

def main():
    st.title("📊 因果関係と疑似相関分析ツール")
    st.caption("Created by Dit-Lab.(Daiki ITO)")
    st.caption("Supported by Tomoaki ATSUMI")
    
    st.markdown("""
    このアプリケーションは、データの相関関係を分析し、因果関係と疑似相関を区別するための補助ツールです。
    統計的相関があっても、必ずしも因果関係があるとは限らないことを理解し、適切な解釈を行うためのガイダンスを提供します。
    """)
    
    # Add educational content about spurious correlation
    with st.expander("📚 疑似相関（擬似相関）のワンポイントレッスン"):
        st.markdown("""
        ### 疑似相関とは
        疑似相関とは、2つの変数の間に相関関係があるように見えるが、実際には両方に影響を与える**第3の要因（交絡因子）**が存在するために生じる、見かけ上の相関のことです。
        
        ### 📊 具体例で理解しよう
        
        **例1：アイスクリームの売上と水難事故の関係**
        
        | 時期 | アイスクリーム売上 | 水難事故件数 | 気温 |
        |------|-------------------|-------------|------|
        | 1月  | 少ない            | 少ない      | 低い |
        | 7月  | 多い              | 多い        | 高い |
        
        一見すると「アイスクリームの売上が増えると水難事故が増える」という相関があるように見えますが...
        
        ❌ **間違った解釈**
        ```
        アイスクリーム売上 → 水難事故
        （アイスを食べると水難事故に遭う？）
        ```
        
        ✅ **正しい理解**
        ```
                    気温（交絡因子）
                     ↙        ↘
        アイスクリーム売上    水難事故件数
        ```
        
        **真の原因は「気温」**です。気温が高いと：
        - アイスクリームがよく売れる
        - 水遊びをする人が増えて水難事故が増える
        
        ### 💡 重要なポイント
        **「相関は必ずしも因果を意味しない」**という点に注意が必要です。
        
        データ分析では、相関関係を見つけた時に：
        1. 第三の変数（交絡因子）が存在しないか検討する
        2. 時間的な前後関係を確認する
        3. 理論的・科学的な根拠があるか考える
        4. 実験や追加データで検証する
        
        このような視点を持つことで、より適切な結論を導くことができます。
        """)
    
    # File upload section
    st.header("📁 データのアップロード")
    uploaded_file = st.file_uploader(
        "Excel (.xlsx) または CSV (.csv) ファイルをアップロードしてください",
        type=['xlsx', 'csv'],
        help="分析したいデータファイルを選択してください"
    )
    
    # Demo data checkbox (placed below upload form as requested)
    use_demo_data = st.checkbox(
        "デモデータを使用する",
        value=False,
        help="サンプルデータを使用して機能を試すことができます"
    )
    
    # Load data
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success(f"✅ ファイルが正常に読み込まれました: {uploaded_file.name}")
            st.session_state.df = df
        except Exception as e:
            st.error(f"❌ ファイルの読み込みに失敗しました: {str(e)}")
            return
            
    elif use_demo_data:
        try:
            df = pd.read_excel('demo_data.xlsx')
            st.success("✅ デモデータが読み込まれました")
            st.session_state.df = df
            
            # Show information about demo data
            with st.expander("📖 デモデータについて"):
                st.markdown("""
                このデモデータは**血圧と年収の疑似相関**を主な例として設計されています：
                
                ### 🎯 メインテーマ: 血圧と年収の関係
                
                **見かけの相関:**
                - 血圧 ↔ 年収 に正の相関が見られます
                
                **実際のメカニズム:**
                - 血圧が高い → 年齢が高い → 年収が高い
                - つまり「年齢」が第三の変数（交絡因子）となっています
                
                **含まれる変数:**
                - **年齢** (20-70歳): 血圧と年収の両方に影響
                - **血圧** (mmHg): 年齢とともに上昇
                - **年収** (円): 年齢とともに増加（50代でピーク）
                - **教育レベル** (1-4): 年収に影響
                - **週間運動時間**: 血圧を下げる効果
                - **BMI**: 血圧に影響
                - **仕事のストレス** (1-10): 血圧に影響
                - **性別**: 年収格差を反映
                - **靴サイズ**: 性別との疑似相関例
                - **睡眠時間**: 血圧に影響
                
                ### 💡 学習ポイント
                この例を通じて、相関関係があっても直接的な因果関係とは限らないことを理解できます。
                血圧と年収の間には直接的な因果関係はありませんが、年齢という共通の要因により相関が生じています。
                """)
        except Exception as e:
            st.error(f"❌ デモデータの読み込みに失敗しました: {str(e)}")
            return
    else:
        st.info("👆 ファイルをアップロードするか、デモデータを使用してください")
        return
    
    # Data preview
    if 'df' in st.session_state:
        df = st.session_state.df
        
        st.header("📋 データプレビュー")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("サンプル数", len(df))
        with col2:
            st.metric("変数数", len(df.columns))
        with col3:
            st.metric("欠損値", df.isnull().sum().sum())
        
        with st.expander("データの詳細を確認"):
            st.dataframe(df.head(10))
            st.subheader("基本統計量")
            st.dataframe(df.describe())
        
        # Variable selection
        st.header("🎯 変数選択")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            st.error("❌ 数値変数が2つ以上必要です")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            x_variable = st.selectbox(
                "X軸の変数を選択",
                numeric_cols,
                help="独立変数（説明変数）として扱いたい変数"
            )
        
        with col2:
            y_variable = st.selectbox(
                "Y軸の変数を選択",
                [col for col in numeric_cols if col != x_variable],
                help="従属変数（被説明変数）として扱いたい変数"
            )
        
        if x_variable and y_variable:
            # Remove missing values for the selected variables
            analysis_df = df[[x_variable, y_variable]].dropna()
            
            if len(analysis_df) < 10:
                st.warning("⚠️ 有効なデータが少なすぎます（10件未満）")
                return
            
            # Analysis section
            st.header("📈 相関分析")
            
            # Create scatter plot
            fig, metrics = create_scatter_plot(analysis_df, x_variable, y_variable)
            st.plotly_chart(fig, use_container_width=True)
            
            # Display correlation metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Pearson相関係数", f"{metrics['pearson_r']:.3f}")
            with col2:
                st.metric("Spearman相関係数", f"{metrics['spearman_r']:.3f}")
            with col3:
                st.metric("決定係数 (R²)", f"{metrics['r_squared']:.3f}")
            with col4:
                p_value_text = "< 0.001" if metrics['pearson_p'] < 0.001 else f"{metrics['pearson_p']:.3f}"
                st.metric("p値", p_value_text)
            
            # Causation analysis
            indicators = analyze_causation_indicators(analysis_df, x_variable, y_variable)
            display_causation_guidance(x_variable, y_variable, indicators)
            
            # Additional visualizations
            st.header("📊 追加の可視化")
            
            tab1, tab2, tab3 = st.tabs(["相関行列", "分布比較", "残差分析"])
            
            with tab1:
                if len(numeric_cols) > 2:
                    selected_for_heatmap = st.multiselect(
                        "相関行列に含める変数を選択",
                        numeric_cols,
                        default=[x_variable, y_variable],
                        max_selections=10
                    )
                    
                    if len(selected_for_heatmap) >= 2:
                        heatmap_fig = create_correlation_heatmap(df, selected_for_heatmap)
                        st.plotly_chart(heatmap_fig, use_container_width=True)
                else:
                    st.info("相関行列の表示には3つ以上の数値変数が必要です")
            
            with tab2:
                fig_dist = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=[f"{x_variable}の分布", f"{y_variable}の分布"]
                )
                
                fig_dist.add_trace(
                    go.Histogram(x=analysis_df[x_variable], name=x_variable),
                    row=1, col=1
                )
                fig_dist.add_trace(
                    go.Histogram(x=analysis_df[y_variable], name=y_variable),
                    row=1, col=2
                )
                
                fig_dist.update_layout(title="変数の分布")
                st.plotly_chart(fig_dist, use_container_width=True)
            
            with tab3:
                if len(analysis_df) > 10:
                    # Linear regression for residual analysis
                    lr = LinearRegression()
                    X_reshaped = analysis_df[x_variable].values.reshape(-1, 1)
                    y_pred = lr.fit(X_reshaped, analysis_df[y_variable]).predict(X_reshaped)
                    residuals = analysis_df[y_variable] - y_pred
                    
                    fig_residuals = make_subplots(
                        rows=1, cols=2,
                        subplot_titles=["残差プロット", "残差のQ-Qプロット"]
                    )
                    
                    # Residual plot
                    fig_residuals.add_trace(
                        go.Scatter(
                            x=y_pred, y=residuals,
                            mode='markers',
                            name='残差'
                        ),
                        row=1, col=1
                    )
                    
                    # Add horizontal line at y=0
                    fig_residuals.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=1)
                    
                    # Q-Q plot
                    qq_fig = ff.create_qq(residuals, sample=residuals, title="")
                    for trace in qq_fig.data:
                        fig_residuals.add_trace(trace, row=1, col=2)
                    
                    fig_residuals.update_layout(
                        title="残差分析",
                        xaxis_title="予測値",
                        yaxis_title="残差"
                    )
                    
                    st.plotly_chart(fig_residuals, use_container_width=True)
                    
                    st.markdown("""
                    **残差分析の見方:**
                    - 左図: 残差が予測値に対してランダムに分散していれば線形関係が適切
                    - 右図: 点が対角線上に並んでいれば残差が正規分布に従う
                    """)

if __name__ == "__main__":
    main()
