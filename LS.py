import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

st.set_page_config(
    page_title="My Library Stats Page",
    page_icon="📚",
    layout="wide"
)

st.title("📚 My Awesome Library Stats Page!")
st.markdown("Let's look at some cool numbers about our library's books!")

@st.cache_data
def load_library_data(file_name='library_data.csv'):
    my_data_table = pd.read_csv(file_name)
    my_data_table['issue_date'] = pd.to_datetime(my_data_table['issue_date'])
    my_data_table['due_date'] = pd.to_datetime(my_data_table['due_date'])
    my_data_table['return_date'] = pd.to_datetime(my_data_table['return_date'])
    return my_data_table

df = load_library_data()

st.sidebar.header("Tweak the Numbers Here!")

earliest_date = df['issue_date'].min().date()
latest_date = df['issue_date'].max().date()

chosen_date_range = st.sidebar.slider(
    "When were the books issued? Pick a date range:",
    min_value=earliest_date,
    max_value=latest_date,
    value=(earliest_date, latest_date)
)

start_date_filter, end_date_filter = pd.to_datetime(chosen_date_range[0]), pd.to_datetime(chosen_date_range[1])
filtered_df = df[(df['issue_date'] >= start_date_filter) & (df['issue_date'] <= end_date_filter)].copy()

all_the_genres = df['genre'].unique()
selected_genres = st.sidebar.multiselect(
    "Which book types (genres) do you want to see?",
    options=all_the_genres,
    default=all_the_genres
)
if selected_genres:
    filtered_df = filtered_df[filtered_df['genre'].isin(selected_genres)]

all_the_borrower_types = df['borrower_type'].unique()
selected_borrower_types = st.sidebar.multiselect(
    "Who borrowed the books? (e.g., Student, Teacher)",
    options=all_the_borrower_types,
    default=all_the_borrower_types
)
if selected_borrower_types:
    filtered_df = filtered_df[filtered_df['borrower_type'].isin(selected_borrower_types)]

if 'student_batch' in df.columns:
    all_the_batches = df['student_batch'].unique()
    selected_batches = st.sidebar.multiselect(
        "Which student batch? (e.g., 2022, 2023)",
        options=all_the_batches,
        default=all_the_batches
    )
    if selected_batches:
        filtered_df = filtered_df[filtered_df['student_batch'].isin(selected_batches)]

if 'student_major' in df.columns:
    all_the_majors = df['student_major'].unique()
    selected_majors = st.sidebar.multiselect(
        "Which student major?",
        options=all_the_majors,
        default=all_the_majors
    )
    if selected_majors:
        filtered_df = filtered_df[filtered_df['student_major'].isin(selected_majors)]

st.header("Quick Numbers!")

col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    total_books = len(filtered_df)
    st.metric("Total Books Given Out", total_books)

with col_b:
    how_many_unique_people = filtered_df['borrower_id'].nunique()
    st.metric("Different People Who Borrowed", how_many_unique_people)

with col_c:
    books_not_returned_yet = filtered_df[filtered_df['return_date'].isna()].shape[0]
    st.metric("Books Still Not Returned", books_not_returned_yet)

with col_d:
    late_books_count = filtered_df[
        (filtered_df['overdue_status'] == 'Overdue') |
        (filtered_df['overdue_status'] == 'Returned Late')
    ].shape[0]
    st.metric("Late Books (Past Due/Returned Late)", late_books_count)

st.header("How Books Are Issued Over Time")

st.subheader("Books Borrowed Every Month")
books_each_month = filtered_df.groupby(pd.Grouper(key='issue_date', freq='M')).size().reset_index(name='count')
fig1, ax1 = plt.subplots(figsize=(8, 4))
ax1.plot(books_each_month['issue_date'], books_each_month['count'], marker='o')
ax1.set_title('Number of Books Issued Each Month')
ax1.set_xlabel('Date')
ax1.set_ylabel('Number of Times Issued')
plt.xticks(rotation=45)
plt.grid(True)
st.pyplot(fig1)

st.subheader("Our 10 Most Borrowed Books")
most_popular_books = filtered_df['book_title'].value_counts().head(10)
fig2, ax2 = plt.subplots(figsize=(8, 5))
sns.barplot(x=most_popular_books.values, y=most_popular_books.index, ax=ax2, palette='viridis')
ax2.set_title('Top 10 Books People Love to Borrow')
ax2.set_xlabel('How Many Times Borrowed')
ax2.set_ylabel('Book Title')
st.pyplot(fig2)

st.subheader("What Kinds of Books Do We Have?")
genre_breakdown = filtered_df['genre'].value_counts()
fig3, ax3 = plt.subplots(figsize=(6, 6))
ax3.pie(genre_breakdown, labels=genre_breakdown.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('pastel'))
ax3.set_title('Breakdown of Books by Genre')
ax3.axis('equal')
st.pyplot(fig3)

st.subheader("Who Borrows Our Books?")
borrower_type_breakdown = filtered_df['borrower_type'].value_counts()
fig4, ax4 = plt.subplots(figsize=(7, 5))
sns.barplot(x=borrower_type_breakdown.index, y=borrower_type_breakdown.values, ax=ax4, palette='deep')
ax4.set_title('Books Issued by Borrower Category')
ax4.set_xlabel('Borrower Category')
ax4.set_ylabel('Number of Books Borrowed')
st.pyplot(fig4)

if 'borrower_age_group' in filtered_df.columns:
    st.subheader("Books Borrowed by Age Group")
    age_group_breakdown = filtered_df['borrower_age_group'].value_counts().sort_index()
    fig5, ax5 = plt.subplots(figsize=(7, 5))
    sns.barplot(x=age_group_breakdown.index, y=age_group_breakdown.values, ax=ax5, palette='dark')
    ax5.set_title('Books Issued by Borrower Age Group')
    ax5.set_xlabel('Age Group')
    ax5.set_ylabel('Number of Books Borrowed')
    st.pyplot(fig5)

st.subheader("Overdue Book Status")
overdue_status_counts = filtered_df['overdue_status'].value_counts()
fig6, ax6 = plt.subplots(figsize=(6, 6))
ax6.pie(overdue_status_counts, labels=overdue_status_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('rocket'))
ax6.set_title('Distribution of Overdue Status')
ax6.axis('equal')
st.pyplot(fig6)

st.subheader("How Long Books Are Borrowed (Average by Genre)")
avg_loan_days_by_genre = filtered_df.groupby('genre')['days_on_loan'].mean().sort_values(ascending=False)
fig7, ax7 = plt.subplots(figsize=(8, 5))
sns.barplot(x=avg_loan_days_by_genre.values, y=avg_loan_days_by_genre.index, ax=ax7, palette='cubehelix')
ax7.set_title('Average Days Books Are Kept, by Genre')
ax7.set_xlabel('Average Days on Loan')
ax7.set_ylabel('Book Genre')
st.pyplot(fig7)

st.header("See the Raw Data (Filtered!)")
st.dataframe(filtered_df)

def convert_df_to_excel(some_dataframe):
    output_buffer = io.BytesIO()
    with pd.ExcelWriter(output_buffer, engine='xlsxwriter') as writer_object:
        some_dataframe.to_excel(writer_object, index=False, sheet_name='Filtered_Library_Data')
    excel_data_bytes = output_buffer.getvalue()
    return excel_data_bytes

excel_ready_data = convert_df_to_excel(filtered_df)

st.download_button(
    label="Click to Download Filtered Data as Excel!",
    data=excel_ready_data,
    file_name="my_library_filtered_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)