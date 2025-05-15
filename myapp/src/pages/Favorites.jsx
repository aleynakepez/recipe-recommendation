import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import API from "../api/api";

function Favorites() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    API.get("users/favorites/")
      .then((res) => {
        setFavorites(res.data.results);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Favoriler alınamadı:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-[#bcc0e5] to-white text-center pt-10 text-lg text-gray-800">
        Loading favorites...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#bcc0e5] to-white">
      <div className="max-w-4xl mx-auto py-10 px-4">
        {/* Başlık */}
        <div className="flex justify-center mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-green-200 to-blue-300 text-black px-6 py-2 rounded shadow">
            My Favorite Recipes
          </h1>
        </div>

        {/* İçerik */}
        {favorites.length === 0 ? (
          <p className="text-center text-gray-600">No favorite recipes yet.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {favorites.map((recipe) => (
              <Link
                to={`/recipes/${recipe.id}`}
                key={recipe.id}
                className="bg-white shadow rounded-lg p-4 hover:shadow-lg transition cursor-pointer block"
              >
                <img
                  src={recipe.image || "/assets/default.jpg"}
                  alt={recipe.title}
                  className="w-full h-40 object-cover rounded mb-4"
                />
                <h2 className="text-xl font-bold mb-2">{recipe.title}</h2>
                <p className="text-sm text-gray-600 mb-2">{recipe.description}</p>
                <p className="text-sm text-gray-500 mb-2">
                  <strong>Prep:</strong> {recipe.prep_time} min | <strong>Cook:</strong> {recipe.cook_time} min |{" "}
                  <strong>Servings:</strong> {recipe.servings}
                </p>
                <ul className="text-sm text-gray-700">
                  {recipe.ingredients.map((ing, i) => (
                    <li key={i}>• {ing.amount} {ing.unit} {ing.ingredient_name}</li>
                  ))}
                </ul>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Favorites;

