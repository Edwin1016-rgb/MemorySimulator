import axios from 'axios';

const BASE_URL = "http://localhost:5000"; // o tu host de Flask

export const iniciarSimulacion = () => axios.get(`${BASE_URL}/iniciar`);
export const siguienteTick = () => axios.get(`${BASE_URL}/tick`);
export const resetSimulacion = () => axios.get(`${BASE_URL}/reset`);
