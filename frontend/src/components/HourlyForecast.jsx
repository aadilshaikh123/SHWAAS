import { motion } from 'framer-motion'
import { Clock, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { useState } from 'react'

function HourlyForecast({ darkMode, hourlyData }) {
    const [selectedHour, setSelectedHour] = useState(null)

    const getAQIColor = (aqi) => {
        if (aqi <= 50) return darkMode ? 'bg-green-500/20 text-green-400 border-green-500/30' : 'bg-green-100 text-green-700 border-green-300'
        if (aqi <= 100) return darkMode ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' : 'bg-yellow-100 text-yellow-700 border-yellow-300'
        if (aqi <= 150) return darkMode ? 'bg-orange-500/20 text-orange-400 border-orange-500/30' : 'bg-orange-100 text-orange-700 border-orange-300'
        if (aqi <= 200) return darkMode ? 'bg-red-500/20 text-red-400 border-red-500/30' : 'bg-red-100 text-red-700 border-red-300'
        return darkMode ? 'bg-teal-500/20 text-teal-400 border-teal-500/30' : 'bg-teal-100 text-teal-700 border-teal-300'
    }

    const getAQIGradient = (aqi) => {
        if (aqi <= 50) return 'from-green-500 to-emerald-500'
        if (aqi <= 100) return 'from-yellow-500 to-amber-500'
        if (aqi <= 150) return 'from-orange-500 to-red-500'
        if (aqi <= 200) return 'from-red-500 to-rose-500'
        return 'from-purple-500 to-pink-500'
    }

    const getAQICategory = (aqi) => {
        if (aqi <= 50) return 'Good'
        if (aqi <= 100) return 'Moderate'
        if (aqi <= 150) return 'Unhealthy for Sensitive'
        if (aqi <= 200) return 'Unhealthy'
        if (aqi <= 300) return 'Very Unhealthy'
        return 'Hazardous'
    }

    const getTrend = (current, previous) => {
        if (!previous) return null
        const diff = current - previous
        if (Math.abs(diff) < 5) return { icon: Minus, text: 'Stable', color: 'text-gray-500' }
        if (diff > 0) return { icon: TrendingUp, text: `+${diff}`, color: 'text-red-500' }
        return { icon: TrendingDown, text: `${diff}`, color: 'text-green-500' }
    }

    const getTimeOfDay = (hour) => {
        if (hour >= 5 && hour < 12) return { emoji: '🌅', label: 'Morning' }
        if (hour >= 12 && hour < 17) return { emoji: '☀️', label: 'Afternoon' }
        if (hour >= 17 && hour < 20) return { emoji: '🌆', label: 'Evening' }
        return { emoji: '🌙', label: 'Night' }
    }

    if (!hourlyData || hourlyData.length === 0) {
        return null
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className={`p-6 rounded-2xl ${darkMode ? 'bg-white/5' : 'bg-white/80'
                } backdrop-blur-sm border ${darkMode ? 'border-white/10' : 'border-gray-200'
                }`}
        >
            {/* Header */}
            <div className="flex items-center gap-3 mb-6">
                <Clock className={`w-6 h-6 ${darkMode ? 'text-blue-400' : 'text-blue-600'}`} />
                <h3 className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                    24-Hour Forecast
                </h3>
                <span className={`text-sm px-3 py-1 rounded-full ${darkMode ? 'bg-blue-900/30 text-blue-300' : 'bg-blue-100 text-blue-700'
                    }`}>
                    ML Predicted
                </span>
            </div>

            {/* Hourly Timeline */}
            <div className="relative">
                {/* Scrollable container */}
                <div className="overflow-x-auto pb-4 -mx-2 px-2">
                    <div className="flex gap-3 min-w-max">
                        {hourlyData.map((hour, index) => {
                            const timeOfDay = getTimeOfDay(hour.hour)
                            const trend = getTrend(hour.aqi, hourlyData[index - 1]?.aqi)
                            const isSelected = selectedHour === index

                            return (
                                <motion.button
                                    key={index}
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: index * 0.02 }}
                                    onClick={() => setSelectedHour(isSelected ? null : index)}
                                    className={`flex-shrink-0 w-32 p-4 rounded-xl border-2 transition-all duration-200 ${isSelected
                                            ? `${getAQIColor(hour.aqi)} border-current shadow-lg scale-105`
                                            : darkMode
                                                ? 'bg-white/5 border-white/10 hover:bg-white/10'
                                                : 'bg-white/60 border-gray-200 hover:bg-white'
                                        }`}
                                >
                                    {/* Time */}
                                    <div className={`text-sm font-bold mb-2 ${isSelected ? '' : darkMode ? 'text-gray-300' : 'text-gray-700'
                                        }`}>
                                        {hour.time}
                                    </div>

                                    {/* Time of day */}
                                    <div className="text-xs mb-3 opacity-70">
                                        {timeOfDay.emoji} {timeOfDay.label}
                                    </div>

                                    {/* AQI Badge */}
                                    <div className={`mb-3 p-2 rounded-lg bg-gradient-to-br ${getAQIGradient(hour.aqi)} text-white`}>
                                        <div className="text-xs font-bold opacity-90">AQI</div>
                                        <div className="text-2xl font-black">{hour.aqi}</div>
                                    </div>

                                    {/* Trend */}
                                    {trend && (
                                        <div className={`flex items-center justify-center gap-1 text-xs ${trend.color}`}>
                                            <trend.icon className="w-3 h-3" />
                                            <span className="font-semibold">{trend.text}</span>
                                        </div>
                                    )}

                                    {/* Weather */}
                                    <div className={`mt-3 pt-3 border-t text-xs space-y-1 ${isSelected
                                            ? 'border-current/30'
                                            : darkMode
                                                ? 'border-white/10 text-gray-400'
                                                : 'border-gray-200 text-gray-600'
                                        }`}>
                                        <div>🌡️ {hour.temp}°C</div>
                                        <div>💧 {hour.humidity}%</div>
                                        <div>💨 {hour.wind} km/h</div>
                                    </div>
                                </motion.button>
                            )
                        })}
                    </div>
                </div>

                {/* Scroll hint */}
                <div className={`text-center mt-4 text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'
                    }`}>
                    ← Scroll to see all hours →
                </div>
            </div>

            {/* Selected Hour Details */}
            {selectedHour !== null && (
                <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className={`mt-6 p-6 rounded-xl border-2 ${getAQIColor(hourlyData[selectedHour].aqi)
                        }`}
                >
                    <div className="flex items-center justify-between mb-4">
                        <h4 className="text-lg font-bold">
                            {hourlyData[selectedHour].time} - {getAQICategory(hourlyData[selectedHour].aqi)}
                        </h4>
                        <button
                            onClick={() => setSelectedHour(null)}
                            className="text-sm opacity-70 hover:opacity-100"
                        >
                            ✕ Close
                        </button>
                    </div>

                    {/* Pollutants Grid */}
                    {hourlyData[selectedHour].pollutants && (
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                            {Object.entries(hourlyData[selectedHour].pollutants).map(([name, data]) => (
                                <div
                                    key={name}
                                    className={`p-3 rounded-lg ${darkMode ? 'bg-white/5' : 'bg-white/50'
                                        }`}
                                >
                                    <div className="text-xs font-bold opacity-70 mb-1">{name}</div>
                                    <div className="text-lg font-black">
                                        {data.value}
                                        <span className="text-xs font-normal ml-1 opacity-70">
                                            {data.unit}
                                        </span>
                                    </div>
                                    <div className="text-xs mt-1">
                                        <span className="opacity-70">AQI: </span>
                                        <span className="font-bold">{data.aqi}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </motion.div>
            )}

            {/* Summary Stats */}
            <div className={`mt-6 grid grid-cols-3 gap-4 p-4 rounded-xl ${darkMode ? 'bg-white/5' : 'bg-gray-50'
                }`}>
                <div className="text-center">
                    <div className={`text-xs mb-1 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                        Average AQI
                    </div>
                    <div className={`text-2xl font-black ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                        {Math.round(hourlyData.reduce((sum, h) => sum + h.aqi, 0) / hourlyData.length)}
                    </div>
                </div>
                <div className="text-center">
                    <div className={`text-xs mb-1 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                        Peak AQI
                    </div>
                    <div className={`text-2xl font-black ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                        {Math.max(...hourlyData.map(h => h.aqi))}
                    </div>
                </div>
                <div className="text-center">
                    <div className={`text-xs mb-1 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                        Best Hour
                    </div>
                    <div className={`text-2xl font-black ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                        {hourlyData.reduce((min, h) => h.aqi < min.aqi ? h : min).time.split(' ')[0]}
                    </div>
                </div>
            </div>
        </motion.div>
    )
}

export default HourlyForecast
