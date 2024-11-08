import re
import pandas as pd


def preprocess(data):
    pattern = '\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2}\s?[a-zA-Z]{2} -\s'
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    cleaned_dates = [text.replace('\u202f', ' ') for text in dates]

    # dataframe with user_message and date
    df = pd.DataFrame({'user_message': messages, 'message_date': cleaned_dates})
    df['message_date'] = pd.to_datetime(df['message_date'], format='%m/%d/%y, %I:%M %p - ')

    # separating messages by user and time
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])
    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)
    df.rename(columns={'message_date': 'date'}, inplace=True)

    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['day_name'] = df['date'].dt.day_name()
    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str("00"))
        elif hour == 0:
            period.append(str("00") + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))
    df['period'] = period

    return df
