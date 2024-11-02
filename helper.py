import pandas as pd
from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import emoji


def fetch_stats(selected_user, df):
    if selected_user != 'All Users':
        df = df[df['user'] == selected_user]
    df = df[df['user'] != 'group_notification']
    # fetch the no. of messages
    num_messages = df.shape[0]
    # fetch no. of media shared
    num_media = df[df['message'] == '<Media omitted>\n'].shape[0]
    df = df[df['message'] != '<Media omitted>\n']
    df = df[df['message'] != 'null\n']
    words = []
    for message in df['message']:
        words.extend(message.split())
    # fetch the no. of words
    num_words = len(words)
    # fetch no. of links
    extractor = URLExtract()

    # Apply URL extraction to each message and flatten the result
    df['links'] = df['message'].apply(extractor.find_urls)
    links = [url for sublist in df['links'] for url in sublist]
    num_links = len(links)

    return num_messages, num_words, num_media, num_links


def most_active_users(df):
    x = df['user'].value_counts().head()
    y = round((df['user'].value_counts() / df.shape[0]) * 100, 2)
    return x, y


def create_wordcloud(selected_user, df):
    if selected_user != 'All Users':
        df = df[df['user'] == selected_user]
    df = df[df['message'] != '<Media omitted>\n']
    wc = WordCloud(
        width=500,
        height=500,
        min_font_size=10,
        background_color='white'
    )
    df_wc = wc.generate(df['message'].str.cat(sep=" "))
    return df_wc


def most_common_words(selected_user, df):
    if selected_user != 'All Users':
        df = df[df['user'] == selected_user]
    df = df[df['user'] != 'group_notification']
    df = df[df['message'] != '<Media omitted>\n']
    df = df[df['message'] != 'null\n']
    words = []
    for message in df['message']:
        words.extend(message.lower().split())
    most_common_df = pd.DataFrame(Counter(words).most_common(20), columns=["Word", "Frequency"])

    return most_common_df


def emoji_helper(selected_user, df):
    if selected_user != 'All Users':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])
    len_emoji = len(emojis)
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(emojis)), columns=["Emoji", "Frequency"])
    return emoji_df, len_emoji


def monthly_timeline(selected_user, df):
    if selected_user != 'All Users':
        df = df[df['user'] == selected_user]
    df['month_num'] = df['date'].dt.month
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    timeline['time'] = time

    return timeline


def daily_timeline(selected_user, df):

    if selected_user != 'All Users':
        df = df[df['user'] == selected_user]
    df = df[df['user'] != 'group_notification']
    df['day_date'] = df['date'].dt.date
    timeline = df.groupby(['day_date']).count()['message'].reset_index()
    return timeline


def day_activity(selected_user, df):

    if selected_user != 'All Users':
        df = df[df['user'] == selected_user]
    df = df[df['user'] != 'group_notification']
    df['day_date'] = df['date'].dt.date
    df['day_name'] = df['date'].dt.day_name()
    timeline = df.groupby(['day_name', 'day_date']).count()['message'].reset_index()
    timeline = timeline.drop(columns=['day_date'])
    # Group by 'day_name' and calculate the average of 'message_count'
    average_per_day = timeline.groupby('day_name')['message'].mean().reset_index()

    # Rename the column for clarity
    average_per_day.rename(columns={'message': 'avg'}, inplace=True)

    return average_per_day


def month_activity(selected_user, df):

    if selected_user != 'All Users':
        df = df[df['user'] == selected_user]
    df = df[df['user'] != 'group_notification']
    df['day_date'] = df['date'].dt.date
    df['month_name'] = df['date'].dt.month_name()
    timeline = df.groupby(['month_name', 'day_date']).count()['message'].reset_index()
    timeline = timeline.drop(columns=['day_date'])
    # Group by 'day_name' and calculate the average of 'message_count'
    average_per_day = timeline.groupby('month_name')['message'].mean().reset_index()

    # Rename the column for clarity
    average_per_day.rename(columns={'message': 'avg'}, inplace=True)

    return average_per_day


def activity_heatmap(selected_user, df):
    if selected_user != 'All Users':
        df = df[df['user'] == selected_user]

    activity_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return activity_heatmap

