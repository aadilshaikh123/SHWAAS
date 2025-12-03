import { motion } from 'framer-motion'
import { Thermometer, Droplets, Wind, Activity, Sparkles, ExternalLink, ChevronDown, ChevronUp, Calendar } from 'lucide-react'
import { useState } from 'react'
import HourlyForecast from './HourlyForecast'

function ForecastDisplay({ darkMode, result }) {
  const [expandedSearch, setExpandedSearch] = useState(false)
  const [expandedPollutants, setExpandedPollutants] = useState(false)

  const getAQIColor = (aqi) => {
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

  const getAQIIcon = (aqi) => {
    if (aqi <= 50) return '😊'
    if (aqi <= 100) return '😐'
    if (aqi <= 150) return '😷'
    if (aqi <= 200) return '😨'
    return '☠️'
  }

  const DayCard = ({ forecast, label, delay }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className={`p-6 rounded-2xl ${darkMode ? 'bg-white/5' : 'bg-white/80'
        } backdrop-blur-sm border ${darkMode ? 'border-white/10' : 'border-gray-200'
        }`}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Calendar className={`w-5 h-5 ${darkMode ? 'text-purple-400' : 'text-purple-600'}`} />
          <h3 className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
            {label}
          </h3>
        </div>
        {forecast.forecast_time && (
          <div className={`flex items-center gap-2 text-sm px-3 py-1 rounded-full ${darkMode ? 'bg-white/10 text-gray-300' : 'bg-gray-100 text-gray-700'
            }`}>
            <span>🕐</span>
            <span className="font-semibold">{forecast.forecast_time}</span>
          </div>
        )}
      </div>

      {/* Time of day indicator */}
      {forecast.forecast_hour !== undefined && (
        <div className={`text-xs mb-3 px-2 py-1 rounded inline-block ${darkMode ? 'bg-purple-900/30 text-purple-300' : 'bg-purple-100 text-purple-700'
          }`}>
          {forecast.forecast_hour >= 5 && forecast.forecast_hour < 12 ? '🌅 Morning' :
            forecast.forecast_hour >= 12 && forecast.forecast_hour < 17 ? '☀️ Afternoon' :
              forecast.forecast_hour >= 17 && forecast.forecast_hour < 20 ? '🌆 Evening' : '🌙 Night'}
        </div>
      )}

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {/* AQI */}
        <div className={`p-4 rounded-xl bg-gradient-to-br ${getAQIColor(forecast.aqi)} text-white text-center`}>
          <div className="text-xs font-bold mb-1 opacity-90">AQI</div>
          <div className="text-3xl font-black mb-1">{forecast.aqi}</div>
          <div className="text-xs font-bold">{getAQICategory(forecast.aqi)}</div>
          <div className="text-2xl mt-1">{getAQIIcon(forecast.aqi)}</div>
        </div>

        {/* Temperature */}
        <div className={`p-4 rounded-xl text-center ${darkMode ? 'bg-orange-900/30 text-orange-300' : 'bg-orange-50 text-orange-700'
          }`}>
          <Thermometer className="w-4 h-4 mx-auto mb-1 opacity-70" />
          <div className="text-xs font-bold mb-1 opacity-70">TEMP</div>
          <div className="text-2xl font-black">{forecast.temp.toFixed(1)}°C</div>
        </div>

        {/* Humidity */}
        <div className={`p-4 rounded-xl text-center ${darkMode ? 'bg-blue-900/30 text-blue-300' : 'bg-blue-50 text-blue-700'
          }`}>
          <Droplets className="w-4 h-4 mx-auto mb-1 opacity-70" />
          <div className="text-xs font-bold mb-1 opacity-70">HUMIDITY</div>
          <div className="text-2xl font-black">{forecast.humidity.toFixed(0)}%</div>
        </div>

        {/* Wind */}
        <div className={`p-4 rounded-xl text-center ${darkMode ? 'bg-teal-900/30 text-teal-300' : 'bg-teal-50 text-teal-700'
          }`}>
          <Wind className="w-4 h-4 mx-auto mb-1 opacity-70" />
          <div className="text-xs font-bold mb-1 opacity-70">WIND</div>
          <div className="text-2xl font-black">{forecast.wind.toFixed(1)}</div>
          <div className="text-xs opacity-70">km/h</div>
        </div>
      </div>
    </motion.div>
  )

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.6 }}
      className="space-y-6"
    >
      {/* City Header */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className={`text-center p-6 rounded-2xl ${darkMode ? 'bg-white/5' : 'bg-white/80'
          } backdrop-blur-sm border ${darkMode ? 'border-white/10' : 'border-gray-200'
          }`}
      >
        <h2 className={`text-3xl font-black mb-2 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
          {result.city}
        </h2>
        <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
          Weather & Air Quality Forecast
        </p>
      </motion.div>

      {/* Today and Tomorrow Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {result.today_forecast && (
          <DayCard forecast={result.today_forecast} label="Today" delay={0.1} />
        )}
        <DayCard forecast={result.forecast} label="Tomorrow" delay={result.today_forecast ? 0.2 : 0.1} />
      </div>

      {/* Hourly Forecast */}
      {result.hourly_forecast && result.hourly_forecast.length > 0 && (
        <HourlyForecast darkMode={darkMode} hourlyData={result.hourly_forecast} />
      )}

      {/* Pollutants Breakdown */}
      {result.forecast.pollutants && Object.keys(result.forecast.pollutants).length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className={`p-6 rounded-2xl ${darkMode ? 'bg-white/5' : 'bg-white/80'
            } backdrop-blur-sm border ${darkMode ? 'border-white/10' : 'border-gray-200'
            }`}
        >
          <button
            onClick={() => setExpandedPollutants(!expandedPollutants)}
            className="w-full flex items-center justify-between mb-4"
          >
            <div className="flex items-center gap-3">
              <Activity className={`w-5 h-5 ${darkMode ? 'text-purple-400' : 'text-purple-600'}`} />
              <h3 className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                Pollutant Details
              </h3>
              {result.forecast.dominant_pollutant && (
                <span className={`text-xs px-3 py-1 rounded-full font-semibold ${darkMode ? 'bg-red-900/50 text-red-300' : 'bg-red-100 text-red-700'
                  }`}>
                  {result.forecast.dominant_pollutant}
                </span>
              )}
            </div>
            {expandedPollutants ? (
              <ChevronUp className={`w-5 h-5 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`} />
            ) : (
              <ChevronDown className={`w-5 h-5 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`} />
            )}
          </button>

          {expandedPollutants && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {Object.entries(result.forecast.pollutants).map(([name, data]) => (
                  <div
                    key={name}
                    className={`p-4 rounded-xl ${darkMode ? 'bg-white/5' : 'bg-gray-50'
                      }`}
                  >
                    <div className={`text-xs font-bold mb-1 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                      {name}
                    </div>
                    <div className={`text-xl font-black mb-1 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                      {data.value}
                      <span className={`text-xs font-normal ml-1 ${darkMode ? 'text-gray-500' : 'text-gray-600'}`}>
                        {data.unit}
                      </span>
                    </div>
                    <div className="text-xs">
                      <span className={darkMode ? 'text-gray-500' : 'text-gray-600'}>AQI: </span>
                      <span className={`font-bold ${data.aqi <= 50 ? 'text-green-500' :
                        data.aqi <= 100 ? 'text-yellow-500' :
                          data.aqi <= 150 ? 'text-orange-500' : 'text-red-500'
                        }`}>
                        {data.aqi}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </motion.div>
      )}

      {/* Summary */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className={`p-6 rounded-2xl ${darkMode ? 'bg-indigo-900/20' : 'bg-indigo-50'
          } border ${darkMode ? 'border-indigo-500/20' : 'border-indigo-200'
          }`}
      >
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className={`w-5 h-5 ${darkMode ? 'text-indigo-400' : 'text-indigo-600'}`} />
          <h3 className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
            Summary
          </h3>
        </div>
        <p className={`leading-relaxed ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
          {result.summary}
        </p>
      </motion.div>

      {/* Advice */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className={`p-6 rounded-2xl ${darkMode ? 'bg-green-900/20' : 'bg-green-50'
          } border ${darkMode ? 'border-green-500/20' : 'border-green-200'
          }`}
      >
        <div className="flex items-center gap-2 mb-3">
          <span className="text-2xl">💡</span>
          <h3 className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
            Health Advice
          </h3>
        </div>
        <p className={`leading-relaxed ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
          {result.advice}
        </p>
      </motion.div>

      {/* Search Results */}
      {result.search_results && result.search_results.results && result.search_results.results.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className={`p-6 rounded-2xl ${darkMode ? 'bg-amber-900/20' : 'bg-amber-50'
            } border ${darkMode ? 'border-amber-500/20' : 'border-amber-200'
            }`}
        >
          <button
            onClick={() => setExpandedSearch(!expandedSearch)}
            className="w-full flex items-center justify-between mb-4"
          >
            <div className="flex items-center gap-2">
              <span className="text-2xl">🔍</span>
              <h3 className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                Latest News
              </h3>
              {result.search_results.total_sources && (
                <span className={`text-xs px-2 py-1 rounded-full ${darkMode ? 'bg-amber-900/50 text-amber-300' : 'bg-amber-200 text-amber-900'
                  }`}>
                  {result.search_results.total_sources} sources
                </span>
              )}
            </div>
            {expandedSearch ? (
              <ChevronUp className={`w-5 h-5 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`} />
            ) : (
              <ChevronDown className={`w-5 h-5 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`} />
            )}
          </button>

          {expandedSearch && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-3"
            >
              {result.search_results.summary && (
                <p className={`text-sm leading-relaxed pb-3 border-b ${darkMode ? 'text-gray-300 border-white/10' : 'text-gray-700 border-gray-200'
                  }`}>
                  {result.search_results.summary}
                </p>
              )}

              <div className="space-y-2">
                {result.search_results.results.slice(0, 5).map((item, index) => (
                  <a
                    key={index}
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`block p-3 rounded-lg transition-all duration-200 ${darkMode
                      ? 'bg-white/5 hover:bg-white/10'
                      : 'bg-white/60 hover:bg-white'
                      }`}
                  >
                    <div className={`font-semibold text-sm mb-1 flex items-start gap-2 ${darkMode ? 'text-amber-300' : 'text-amber-900'
                      }`}>
                      <span className="flex-1">{item.title}</span>
                      <ExternalLink className="w-3 h-3 flex-shrink-0 mt-1 opacity-50" />
                    </div>
                    {item.content && (
                      <p className={`text-xs line-clamp-2 ${darkMode ? 'text-gray-400' : 'text-gray-600'
                        }`}>
                        {item.content}
                      </p>
                    )}
                  </a>
                ))}
              </div>
            </motion.div>
          )}
        </motion.div>
      )}
    </motion.div>
  )
}

export default ForecastDisplay
