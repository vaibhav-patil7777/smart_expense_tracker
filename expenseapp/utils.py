import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
import plotly.express as px
import pandas as pd

def get_monthly_chart(expenses, chart_type='bar'):
    if not expenses:
        return None, None

    df = pd.DataFrame(expenses.values('category', 'amount', 'date'))

    # Pie or Bar
    pie_chart = None
    if chart_type in ['pie', 'bar']:
        fig, ax = plt.subplots()
        data = df.groupby('category')['amount'].sum()
        if chart_type == 'pie':
            ax.pie(data, labels=data.index, autopct='%1.1f%%')
        else:
            data.plot(kind='bar', ax=ax)
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        pie_chart = image_base64
        plt.close()

    # Line chart using Plotly
    plotly_html = None
    if chart_type == 'line':
        df['date'] = pd.to_datetime(df['date'])
        line_df = df.groupby('date')['amount'].sum().reset_index()
        fig = px.line(line_df, x='date', y='amount', title='Daily Expenses Trend')
        plotly_html = fig.to_html(full_html=False)

    return pie_chart, plotly_html
