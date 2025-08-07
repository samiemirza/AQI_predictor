# AQI Predictor - React Frontend

A modern React dashboard for the AQI Prediction System with interactive maps, real-time data visualization, and beautiful UI components.

## 🚀 Features

- **🌍 Interactive World Map** - Click to select locations or search for cities
- **📊 Real-time Predictions** - Beautiful charts and statistics for AQI forecasts
- **🎨 Modern UI** - Built with Ant Design and styled-components
- **📱 Responsive Design** - Works on desktop, tablet, and mobile
- **⚡ Fast Performance** - Optimized React components with lazy loading
- **🔧 Easy Configuration** - Simple API key setup and location selection

## 🛠️ Tech Stack

- **React 18** - Modern UI framework
- **Ant Design** - Professional UI components
- **React Leaflet** - Interactive maps
- **Recharts** - Beautiful data visualizations
- **Styled Components** - CSS-in-JS styling
- **Axios** - HTTP client for API calls

## 📦 Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

## 🔧 Configuration

### API Key Setup

1. Get your OpenWeatherMap API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Set the API key in the dashboard sidebar
3. The key will be stored locally for future use

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:5000
```

## 📱 Usage

### Home Page

1. **Select a Location:**
   - Click on the world map to select any location
   - Use the search bar to find specific cities
   - Major cities are pre-marked on the map

2. **Update Data:**
   - Click "🔄 Update Data" to fetch latest air pollution data
   - This collects 5 days of historical data for the selected location

3. **Train Models:**
   - Click "🤖 Train Models" to train the prediction models
   - Multiple algorithms are tested and the best one is selected

4. **Generate Predictions:**
   - Click "🔮 Generate Predictions" to get 5-day AQI forecasts
   - Results are displayed in beautiful charts and tables

### About Page

- **Project Information** - Complete details about the AQI prediction system
- **Technical Stack** - Frontend and backend technologies used
- **Model Performance** - Current model metrics and performance
- **Use Cases** - Real-world applications of the system

## 🎨 UI Components

### World Map
- Interactive map with clickable markers
- Major cities pre-marked for easy selection
- Custom markers for selected locations
- Responsive design for all screen sizes

### Current AQI Widget
- Real-time air quality display
- Color-coded AQI values
- Progress bars and statistics
- Health impact indicators

### Prediction Widget
- Line charts for AQI forecasts
- Summary statistics (average, max, min)
- Detailed predictions table
- Health alerts for hazardous levels

## 🔌 API Integration

The frontend communicates with the backend through REST API endpoints:

- `GET /api/current-aqi` - Fetch current air quality
- `GET /api/predictions` - Get AQI predictions
- `POST /api/update-data` - Update historical data
- `POST /api/train-models` - Train prediction models
- `POST /api/generate-predictions` - Generate new predictions

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

### Deploy to Netlify

1. Connect your GitHub repository to Netlify
2. Set build command: `npm run build`
3. Set publish directory: `build`
4. Deploy!

### Deploy to Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`
3. Follow the prompts

## 🐛 Development

### Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

### Project Structure

```
frontend/
├── public/                 # Static files
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── Navigation.js
│   │   ├── WorldMap.js
│   │   ├── CurrentAQIWidget.js
│   │   └── PredictionWidget.js
│   ├── pages/             # Page components
│   │   ├── HomePage.js
│   │   └── AboutPage.js
│   ├── services/          # API services
│   │   └── api.js
│   ├── App.js            # Main app component
│   └── index.js          # Entry point
├── package.json
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For questions or issues:
1. Check the documentation
2. Search existing issues
3. Create a new issue with details

---

**Built with ❤️ for better air quality monitoring and prediction** 