import { motion } from 'framer-motion'

function LoadingSkeleton({ darkMode }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.6 }}
            className={`rounded-3xl shadow-2xl p-6 sm:p-8 transition-all duration-300 ${darkMode ? 'glass-dark' : 'glass bg-white/80'
                }`}
        >
            {/* Animated Icon */}
            <div className="text-center mb-8">
                <motion.div
                    animate={{
                        scale: [1, 1.2, 1],
                        rotate: [0, 360],
                    }}
                    transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                    className="text-7xl mb-4 inline-block"
                >
                    🌤️
                </motion.div>
                <p className={`text-lg font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Fetching weather data...
                </p>
            </div>

            {/* Skeleton Metrics Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                {[1, 2, 3, 4].map((i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: i * 0.1 }}
                        className={`text-center p-5 rounded-2xl ${darkMode ? 'bg-white/5' : 'bg-gray-100'
                            }`}
                    >
                        <div className={`h-4 w-20 mx-auto mb-3 rounded animate-shimmer ${darkMode ? 'bg-white/10' : 'bg-gray-200'
                            }`} />
                        <div className={`h-10 w-16 mx-auto mb-2 rounded animate-shimmer ${darkMode ? 'bg-white/10' : 'bg-gray-200'
                            }`} />
                        <div className={`h-3 w-24 mx-auto rounded animate-shimmer ${darkMode ? 'bg-white/10' : 'bg-gray-200'
                            }`} />
                    </motion.div>
                ))}
            </div>

            {/* Skeleton Summary */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className={`mb-4 p-5 rounded-2xl ${darkMode ? 'bg-white/5' : 'bg-gray-100'
                    }`}
            >
                <div className={`h-6 w-32 mb-3 rounded animate-shimmer ${darkMode ? 'bg-white/10' : 'bg-gray-200'
                    }`} />
                <div className={`h-4 w-full mb-2 rounded animate-shimmer ${darkMode ? 'bg-white/10' : 'bg-gray-200'
                    }`} />
                <div className={`h-4 w-3/4 rounded animate-shimmer ${darkMode ? 'bg-white/10' : 'bg-gray-200'
                    }`} />
            </motion.div>

            {/* Skeleton Advice */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className={`p-5 rounded-2xl ${darkMode ? 'bg-white/5' : 'bg-gray-100'
                    }`}
            >
                <div className={`h-6 w-32 mb-3 rounded animate-shimmer ${darkMode ? 'bg-white/10' : 'bg-gray-200'
                    }`} />
                <div className={`h-4 w-full mb-2 rounded animate-shimmer ${darkMode ? 'bg-white/10' : 'bg-gray-200'
                    }`} />
                <div className={`h-4 w-5/6 rounded animate-shimmer ${darkMode ? 'bg-white/10' : 'bg-gray-200'
                    }`} />
            </motion.div>
        </motion.div>
    )
}

export default LoadingSkeleton
