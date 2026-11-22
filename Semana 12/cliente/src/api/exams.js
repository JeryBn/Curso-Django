import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/',
  timeout: 10000,
});

export function setToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Token ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
}

export async function listExams(page, signal) {
  const { data } = await api.get('exams/', { params: { page }, signal });
  return data;
}

export async function createExam(title) {
  const { data } = await api.post('exams/', { title });
  return data;
}

export function deleteExam(id) {
  return api.delete(`exams/${id}/`);
}

export function requestError(error) {
  if (error.response?.status === 401) {
    return 'Introduce un token válido del laboratorio para acceder a la API.';
  }
  if (error.response?.status === 403) {
    return 'La API denegó la operación. Para crear y eliminar usa el token del usuario profe.';
  }
  if (error.response?.status === 404) {
    return 'La API no encontró el registro o la página solicitada.';
  }
  if (!error.response) {
    return 'No se pudo conectar con Django. Comprueba el servidor y el origen autorizado en CORS.';
  }
  return `Django no pudo completar la petición (HTTP ${error.response.status}).`;
}
