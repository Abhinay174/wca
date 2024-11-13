import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import seaborn as sns
import plotly.express as px
import zipfile
import preprocessor
import helper

st.set_page_config(layout="wide")

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a ZIP file", type=["zip"])
if uploaded_file is not None:
    # Open the uploaded ZIP file
    with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
        # Get the list of files in the ZIP
        file_list = zip_ref.namelist()
        
        # Filter for .txt files (assuming there's only one .txt file)
        txt_files = [file for file in file_list if file.endswith('.txt')]
        txt_file_name = txt_files[0]  # Get the first .txt file in the list

        with zip_ref.open(txt_file_name) as file:
            # Read and decode the file content
            data = file.read().decode('utf-8')
        # Display the content of the file (or perform further operations)
        df = preprocessor.preprocess(data)
        st.dataframe(df)
        # fetch  unique users
        user_list = df['user'].unique().tolist()
        user_list.remove('group_notification')
        user_list.sort()
        user_list.insert(0, 'All Users')
        selected_user = st.sidebar.selectbox("Show analysis of ", user_list)

        if st.sidebar.button("Show analysis"):
            num_messages, num_words, num_media, num_links = helper.fetch_stats(selected_user, df)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.header("Total Messages ")
                st.title(num_messages)
            with col2:
                st.header("Total Words ")
                st.title(num_words)
            with col3:
                st.header("Media Shared ")
                st.title(num_media)
            with col4:
                st.header("Links Shared ")
                st.title(num_links)

            # Timeline

            st.title('Daily Analysis')
            timeline = helper.daily_timeline(selected_user, df)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=timeline['day_date'], y=timeline['message'], mode='lines+markers'))
            fig.update_layout(
                title='Timeline of Messages',
                xaxis_title='Date',
                yaxis_title='Messages'
            )
            st.plotly_chart(fig, use_container_width=True)

            st.title('Monthly Analysis')
            timeline = helper.monthly_timeline(selected_user, df)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=timeline['time'], y=timeline['message'], mode='lines+markers', name='Messages'))
            fig.update_layout(
                title='Timeline of Messages',
                xaxis_title='Month-Year',
                yaxis_title='Messages'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Activity Map
            st.title('Activity Analysis')
            col1, col2 = st.columns(2)
            timeline = helper.day_activity(selected_user, df)
            fig1 = go.Figure(data=[go.Bar(x=timeline['day_name'], y=timeline['avg'])])
            fig1.update_layout(
                title='Average Messages Per Day',
                xaxis_title='Day of the Week',
                yaxis_title='Average Messages'
            )
            timeline = helper.month_activity(selected_user, df)
            fig2 = go.Figure(data=[go.Bar(x=timeline['month_name'], y=timeline['avg'])])
            fig2.update_layout(
                title='Average Messages Per Month',
                xaxis_title='Month',
                yaxis_title='Average Messages'
            )
            with col1:
                st.plotly_chart(fig1, use_container_width=True)
            with col2:
                st.plotly_chart(fig2, use_container_width=True)

            # finding the busiest users in the group
            if selected_user == 'All Users':
                st.title('Most Active Users')
                x, y = helper.most_active_users(df)
                name = x.index
                count = x.values

                # Create a bar plot
                fig1 = go.Figure(data=[go.Bar(x=name, y=count)])
                fig1.update_layout(
                    title="Top 5 Users by Count",
                    xaxis_title="User",
                    yaxis_title="Count",
                )

                fig2 = go.Figure(
                    data=[go.Pie(labels=y.index, values=y.values)])

                fig2.update_layout(
                    title="Users by Percentage",
                )

                col1, col2, = st.columns(2)
                with col1:
                    st.plotly_chart(fig1, use_container_width=True)
                with col2:
                    st.plotly_chart(fig2, use_container_width=True)

            # WordCloud

            df_wc = helper.create_wordcloud(selected_user, df)
            fig3, ax = plt.subplots()
            ax.imshow(df_wc, interpolation="lanczos")
            ax.axis("off")
            st.title('WordCloud')
            st.pyplot(fig3)

            most_common_df = helper.most_common_words(selected_user, df)
            st.title('Most Used Words')
            fig4 = go.Figure(data=[go.Bar(x=most_common_df['Word'], y=most_common_df['Frequency'])])
            st.plotly_chart(fig4, use_container_width=True)

            # Emoji Analysis
            emoji_df, len_emoji = helper.emoji_helper(selected_user, df)
            st.title('Emoji Analysis')

            col1, col2 = st.columns([1, 3])
            with col1:
                st.dataframe(emoji_df, use_container_width=True)
            with col2:
                emoji_df['Percentage'] = round((emoji_df['Frequency'] / len_emoji)*100, 1)
                emoji_df = emoji_df.head(10)
                fig5 = go.Figure(
                    data=[
                        go.Pie(
                            labels=emoji_df['Emoji'],
                            values=emoji_df['Percentage'],
                            textinfo='label+value'
                        )
                    ]
                )
                st.plotly_chart(fig5, use_container_width=True)

            st.title("Weekly Activity Map")
            user_heatmap = helper.activity_heatmap(selected_user, df)
            fig, ax = plt.subplots()
            ax = sns.heatmap(user_heatmap)
            st.pyplot(fig)

else:
    st.title("Upload a ZIP file")
