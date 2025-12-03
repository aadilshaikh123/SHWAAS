import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Info, X } from 'lucide-react'
import Header from './components/Header'
import InputForm from './components/InputForm'
import ForecastDisplay from './components/ForecastDisplay'
import LoadingSkeleton from './components/LoadingSkeleton'

function App() {
    const [darkMode, setDarkMode] = useState(() => {
        const saved = localStorage.getItem('darkMode')
        return saved ? JSON.parse(saved) : true
    })

    const [formData, setFormData] = useState({
        city: '',
        lat: null,
        lon: null,
        profile: '',
        useSearch: false
    })

    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [error, setError] = useState(null)
    const [showInfo, setShowInfo] = useState(false)

    useEffect(() => {
        localStorage.setItem('darkMode', JSON.stringify(darkMode))
        document.documentElement.classList.toggle('dark', darkMode)
    }, [darkMode])

    const handleSubmit = async (data) => {
        setLoading(true)
        setError(null)
        setResult(null)

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    city: data.city,
                    lat: data.lat,
                    lon: data.lon,
                    profile: data.profile,
                    use_search: data.useSearch
                })
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || 'Failed to get forecast')
            }

            const resultData = await response.json()
            setResult(resultData)
        } catch (err) {
            setError(err.message || 'An unexpected error occurred')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className={`min-h-screen transition-all duration-700 ${darkMode
            ? 'bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950'
            : 'bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50'
            }`}>
            {/* Animated background elements */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <motion.div
                    className="absolute top-20 left-10 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
                    animate={{
                        x: [0, 100, 0],
                        y: [0, 50, 0],
                    }}
                    transition={{
                        duration: 20,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                />
                <motion.div
                    className="absolute top-40 right-10 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
                    animate={{
                        x: [0, -100, 0],
                        y: [0, 100, 0],
                    }}
                    transition={{
                        duration: 25,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                />
                <motion.div
                    className="absolute bottom-20 left-1/2 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
                    animate={{
                        x: [0, 50, 0],
                        y: [0, -50, 0],
                    }}
                    transition={{
                        duration: 15,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                />
            </div>

            <div className="relative z-10 container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 max-w-6xl">
                {/* Info Button - Top Right */}
                <motion.button
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setShowInfo(true)}
                    className={`fixed top-6 right-6 p-3 rounded-full shadow-lg transition-all z-40 ${darkMode
                        ? 'bg-white/10 hover:bg-white/20 text-white backdrop-blur-sm'
                        : 'bg-white hover:bg-gray-50 text-gray-700 border border-gray-200'
                        }`}
                    title="About this app"
                >
                    <Info className="w-5 h-5" />
                </motion.button>

                <Header darkMode={darkMode} setDarkMode={setDarkMode} loading={loading} />

                <div className="mt-8 space-y-6">
                    <InputForm
                        darkMode={darkMode}
                        formData={formData}
                        setFormData={setFormData}
                        onSubmit={handleSubmit}
                        loading={loading}
                        error={error}
                    />

                    <AnimatePresence mode="wait">
                        {loading && !result && (
                            <LoadingSkeleton key="loading" darkMode={darkMode} />
                        )}

                        {result && !loading && (
                            <ForecastDisplay key="result" darkMode={darkMode} result={result} />
                        )}
                    </AnimatePresence>
                </div>

                <motion.footer
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                    className={`text-center mt-16 mb-8 transition-colors duration-300`}
                >
                    <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                        Built by <span className="font-semibold text-purple-500">AADIL SHAIKH</span> for your health babe.. 💜
                    </p>
                </motion.footer>

                {/* Info Popup */}
                <AnimatePresence>
                    {showInfo && (
                        <>
                            {/* Backdrop */}
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                transition={{ duration: 0.3 }}
                                onClick={() => setShowInfo(false)}
                                className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
                            />

                            {/* Popup */}
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95, y: -20 }}
                                animate={{ opacity: 1, scale: 1, y: 0 }}
                                exit={{ opacity: 0, scale: 0.95, y: -20 }}
                                transition={{ duration: 0.2 }}
                                className={`fixed top-20 right-6 w-full max-w-sm p-5 rounded-xl shadow-2xl z-50 ${darkMode ? 'bg-gray-800/95 backdrop-blur-xl border border-white/10' : 'bg-white/95 backdrop-blur-xl border border-gray-200'
                                    }`}
                            >
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                                        Why We're Better
                                    </h3>
                                    <button
                                        onClick={() => setShowInfo(false)}
                                        className={`p-1 rounded-lg transition-colors ${darkMode ? 'hover:bg-white/10 text-gray-400' : 'hover:bg-gray-100 text-gray-600'
                                            }`}
                                    >
                                        <X className="w-4 h-4" />
                                    </button>
                                </div>

                                <div className={`space-y-2 text-sm ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                                    <div>• Real sensor data (80% more accurate)</div>
                                    <div>• AI-powered insights with Gemini</div>
                                    <div>• ML model trained on historical data</div>
                                    <div>• 6 pollutants tracked (EPA standards)</div>
                                    <div>• Regional environmental news</div>
                                    <div>• Personalized health advice</div>
                                </div>

                                <div className={`mt-4 pt-4 border-t ${darkMode ? 'border-white/10' : 'border-gray-200'}`}>
                                    <p className={`text-xs font-semibold mb-2 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                                        Data Sources:
                                    </p>
                                    <div className={`text-xs space-y-1 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                                        <div>• Google Gemini AI</div>
                                        <div>• Tavily Search API</div>
                                        <div>• Open-Meteo Weather API</div>
                                        <div>• OpenAQ Air Quality Sensors</div>
                                        <div>• EPA Air Quality Standards</div>
                                    </div>
                                </div>
                            </motion.div>
                        </>
                    )}
                </AnimatePresence>
            </div>
        </div>
    )
}

export default App
