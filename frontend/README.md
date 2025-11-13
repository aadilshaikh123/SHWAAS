# AgenticWeatherAI Frontend

Modern, glassmorphic React frontend for weather and air quality predictions.

## Features

✨ **Modern Design**
- Glassmorphism effects with backdrop blur
- Smooth animations with Framer Motion
- Gradient backgrounds with animated blobs
- Dark/Light mode toggle
- Responsive design for all devices

🎨 **UI Components**
- Interactive weather cards with hover effects
- Real-time loading skeletons
- Collapsible sections for pollutants and news
- Beautiful gradient color schemes
- Icon-rich interface with Lucide React

## Tech Stack

- **React 19** - Latest React with modern hooks
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Smooth animations
- **Lucide React** - Beautiful icon library

## Getting Started

### Install Dependencies

```bash
npm install
```

### Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx           # App header with dark mode toggle
│   │   ├── InputForm.jsx        # Location input form
│   │   ├── LoadingSkeleton.jsx  # Loading state animation
│   │   └── ForecastDisplay.jsx  # Weather results display
│   ├── App.jsx                  # Main app component
│   ├── main.jsx                 # React entry point
│   └── index.css                # Global styles + Tailwind
├── index.html                   # HTML template
├── vite.config.js              # Vite configuration
├── tailwind.config.js          # Tailwind configuration
└── package.json                # Dependencies
```

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000`:

- `POST /predict` - Get weather forecast and AQI predictions
- `GET /health` - Check backend health status

## Customization

### Colors

Edit `tailwind.config.js` to customize the color palette.

### Animations

Modify animation timings in `src/index.css` and component files.

### Layout

Adjust component layouts in the respective `.jsx` files.

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)
