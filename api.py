from flask import Flask, jsonify
import pandas as pd
import pickle
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)


#author wise recommodation
content_data=pd.read_csv('content.csv')
content_data = content_data.reset_index()
def get_recommendations_books(title, cosine_sim_author):

    indices = pd.Series(content_data.index, index=content_data['original_title'])
    idx = indices[title]

    # Get the pairwsie similarity scores of all books with that book
    sim_scores = list(enumerate(cosine_sim_author[idx]))

    # Sort the books based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar books
    sim_scores = sim_scores[1:11]

    # Get the book indices
    book_indices = [i[0] for i in sim_scores]

    # Return the top 10 most similar books
    return list(content_data['original_title'].iloc[book_indices])

@app.route("/content_based/<string:book>")
def recommendation_system(book):
    pickled_model = pickle.load(open('content.pkl', 'rb'))
    result={
        "recommended_books":[i.strip() for i in get_recommendations_books(book,pickled_model)]
    }
    return jsonify(result)

rating_popular_book_pivot=pd.read_csv('collab.csv')
rating_popular_book_pivot = rating_popular_book_pivot.set_index('title')

def collaborative(book):
    pickled_model = pickle.load(open('collaborative.pkl', 'rb'))
    # rating_popular_book_matrix = csr_matrix(rating_popular_book_pivot.values)
    # model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
    # model_knn.fit(rating_popular_book_matrix)
    distances, indices = pickled_model.kneighbors(rating_popular_book_pivot.loc[book,:].values.reshape(1, -1), n_neighbors = 6)
    recc=[]
    for i in range(0, len(distances.flatten())):
        print(rating_popular_book_pivot.index[indices.flatten()[i]])
        recc.append(rating_popular_book_pivot.index[indices.flatten()[i]])
    return recc




@app.route("/collaborative/<string:book>")
def collaborative_recommendation(book):
    result={
        "recommended_books":collaborative(book)
    }
    return jsonify(result)







if __name__ == "__main__":
    app.run(debug=True)