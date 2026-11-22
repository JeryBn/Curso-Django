export function adaptMovie({ id, title, synopsis, image, rating, classification, showtimes }) {
  return { id: Number(id), title: title.trim(), synopsis, image, rating: Number(rating), classification, showtimes: [...showtimes] };
}
