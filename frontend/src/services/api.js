const API_BASE = import.meta.env.VITE_API_URL || (window.location.hostname === 'localhost' ? 'http://localhost:5000' : '');


const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
});

export const getUserId = () => {
  let userId = localStorage.getItem('agropredict_user_id') || localStorage.getItem('harvestiq_user_id');
  if (!userId) {
    userId = `user_${Math.random().toString(36).substring(2, 15)}`;
    localStorage.setItem('agropredict_user_id', userId);
  }
  return userId;
};

export const analyseFarm = (lat, lng, options = {}) =>
  api.post('/api/farm/analyse', {
    lat,
    lng,
    areaAcres: options.areaAcres,
    soilInputTier: options.soilInputTier,
    manualSoil: options.manualSoil,
    soilReportData: options.soilReportData
  }).then(r => r.data);

export const parseSoilReportOCR = (textContent, sampleType) =>
  api.post('/api/soil-report/ocr', { textContent, sampleType }).then(r => r.data);

export const getWeather = (lat, lng) =>
  api.get(`/api/weather/${lat}/${lng}`).then(r => r.data);

export const getMarketPrices = (state, crop) =>
  api.get(`/api/market/${encodeURIComponent(state)}/${encodeURIComponent(crop)}`).then(r => r.data);

export const getBorewellRisk = (lat, lng) =>
  api.get(`/api/borewell/${lat}/${lng}`).then(r => r.data);

export const saveHistory = (data) =>
  api.post('/api/history/save', data).then(r => r.data);

export const getHistory = (userId) =>
  api.get(`/api/history/${userId || getUserId()}`).then(r => r.data);

export const deleteHistory = (id) =>
  api.delete(`/api/history/${id}`).then(r => r.data);

export const submitHarvestFeedback = (feedbackData) =>
  api.post('/api/history/feedback', feedbackData).then(r => r.data);

export const getHarvestFeedbacks = (userId) =>
  api.get(`/api/history/feedback/${userId || getUserId()}`).then(r => r.data);

export const sendChat = (message, farmData) =>
  api.post('/api/chat', { message, farmData }).then(r => r.data);

export const analyzeVision = (imageB64, cropHint) =>
  api.post('/api/chat/vision', { image: imageB64, cropHint }).then(r => r.data);

export const getChatStatus = () =>
  api.get('/api/chat/status').then(r => r.data).catch(() => ({ online: false, mode: 'limited' }));

export const predictYield = (data) =>
  api.post('/api/crops/predict-yield', data).then(r => r.data);

export default api;

