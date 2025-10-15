import { useState, useRef, useEffect } from 'react'
import { 
  Upload, Activity, Brain, Microscope, Moon, Sun, 
  FileImage, CheckCircle2, Loader2, Zap
} from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import Liver3DViewer from './Liver3DViewer'
import AnalyticsDashboard from './AnalyticsDashboard'
import HipDemo from './HipDemo'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

type Page = 'analysis' | 'dashboard'

function DemoField({ label, value, darkMode }: { label: string; value: string; darkMode: boolean }) {
  return (
    <div>
      <p className={`text-sm mb-1 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
        {label}
      </p>
      <p className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
        {value}
      </p>
    </div>
  )
}

interface AnalysisResult {
  embeddings: {
    confidence: number
    classification: string
    features: string[]
  }
  segmentation: {
    detected: string[]
    area: string
    severity: string
  }
  overlayImageUrl?: string
  gpt5Analysis: string
  metrics: {
    processingTime: string
    accuracy: string
    modelsUsed: number
  }
  demographics?: {
    patient_id: string
    age: number
    gender: string
    ethnicity: string
    study_date: string
  }
}

interface Patient {
  id: string
  filename: string
  label: string
}

interface BatchResult {
  patient_id: string
  success: boolean
  data?: AnalysisResult
  error?: string
}

function App() {
  const [darkMode, setDarkMode] = useState(true)
  const [currentPage, setCurrentPage] = useState<Page>('dashboard')
  const [selectedOrgan, setSelectedOrgan] = useState<'liver' | 'hip'>('liver')
  const [selectedModality, setSelectedModality] = useState('liver-mri')
  const [uploadedImage, setUploadedImage] = useState<string | null>(null)
  const [processing, setProcessing] = useState(false)
  const [analysisStep, setAnalysisStep] = useState(0)
  const [results, setResults] = useState<AnalysisResult | null>(null)
  const [activeTab, setActiveTab] = useState('upload')
  const [useMockData, setUseMockData] = useState(true)
  const [patients, setPatients] = useState<Patient[]>([])
  const [selectedPatient, setSelectedPatient] = useState<string>('')
  const [batchPatients, setBatchPatients] = useState<string[]>([])
  const [batchResults, setBatchResults] = useState<BatchResult[]>([])
  const [batchProcessing, setBatchProcessing] = useState(false)
  const ensureDataUrlPrefix = (url: string | null): string | null => {
    if (!url) return null
    if (url.startsWith('data:')) return url
    if (url.startsWith('base64,')) return `data:image/png;${url}`
    if (url.match(/^[a-zA-Z0-9+/=]+$/)) return `data:image/png;base64,${url}`
    return url
  }

  const safeUploadedImage = ensureDataUrlPrefix(uploadedImage)

  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetch(`${API_URL}/api/config`)
      .then(res => res.json())
      .then(data => setUseMockData(data.useMockData))
      .catch(err => console.error('Config fetch error:', err))
    
    fetch(`${API_URL}/api/patients`)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setPatients(data.patients)
        }
      })
      .catch(err => console.error('Patients fetch error:', err))
  }, [])

  if (currentPage === 'dashboard') {
    return <AnalyticsDashboard darkMode={darkMode} onNavigate={setCurrentPage} />
  }

  const modalities = [
    { id: 'liver-mri', name: 'Liver MRI', icon: Brain },
    { id: 'liver-ct', name: 'Liver CT', icon: Activity },
    { id: 'ultrasound', name: 'Ultrasound', icon: Zap },
    { id: 'pathology', name: 'Pathology', icon: Microscope }
  ]

  const analysisSteps = [
    { name: 'Image Upload', status: 'complete' },
    { name: 'MedImageParse3D Segmentation', status: analysisStep >= 1 ? 'complete' : 'pending' },
    { name: 'GPT-4.1 Analysis', status: analysisStep >= 2 ? 'complete' : 'pending' }
  ]

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setUploadedImage(e.target?.result as string)
        setResults(null)
        setActiveTab('analyze')
      }
      reader.readAsDataURL(file)
    }
  }

  const loadDemoImage = async () => {
    try {
      const formData = new FormData()
      formData.append('modality', selectedModality)
      if (selectedPatient) {
        formData.append('patient_id', selectedPatient)
      }
      
      const response = await fetch(`${API_URL}/api/upload-demo`, {
        method: 'POST',
        body: formData
      })
      
      const data = await response.json()
      console.log('Backend returned imageUrl:', data.imageUrl?.substring(0, 100))
      if (data.success) {
        setUploadedImage(data.imageUrl)
        setResults(null)
        setActiveTab('analyze')
      }
    } catch (error) {
      console.error('Demo load error:', error)
    }
  }

  const dataURLtoBlob = (dataURL: string): Blob => {
    const parts = dataURL.split(',')
    const byteString = atob(parts[1])
    const mimeString = parts[0].split(':')[1].split(';')[0]
    const ab = new ArrayBuffer(byteString.length)
    const ia = new Uint8Array(ab)
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i)
    }
    return new Blob([ab], { type: mimeString })
  }

  const runAnalysis = async () => {
    if (!uploadedImage) return
    
    setProcessing(true)
    setAnalysisStep(0)
    setActiveTab('results')

    try {
      const blob = dataURLtoBlob(safeUploadedImage!)
      
      const formData = new FormData()
      formData.append('image', blob, 'image.png')
      formData.append('modality', selectedModality)
      if (selectedPatient) {
        formData.append('patient_id', selectedPatient)
      }

      for (let step = 1; step <= analysisSteps.length; step++) {
        setAnalysisStep(step)
        await new Promise(resolve => setTimeout(resolve, 1000))
      }

      const analysisResponse = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        body: formData
      })

      if (!analysisResponse.ok) {
        throw new Error('Analysis failed')
      }

      const result = await analysisResponse.json()
      setResults(result.data)
      setAnalysisStep(analysisSteps.length + 1)
    } catch (error) {
      console.error('Analysis error:', error)
      alert('Error processing image. Please try again.')
    } finally {
      setProcessing(false)
    }
  }

  return (
    <div className={`min-h-screen transition-colors duration-300 ${darkMode ? 'bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900' : 'bg-gradient-to-br from-blue-50 via-white to-slate-50'}`}>
      <nav className={`border-b ${darkMode ? 'border-slate-700 bg-slate-800/50' : 'border-gray-200 bg-white/50'} backdrop-blur-sm`}>
        <div className="container mx-auto px-4 py-4 flex gap-4 items-center justify-between">
          <div className="flex gap-4">
            <button
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                currentPage === 'dashboard'
                  ? darkMode ? 'bg-blue-600 text-white' : 'bg-blue-500 text-white'
                  : darkMode ? 'hover:bg-slate-700 text-gray-300' : 'hover:bg-gray-100 text-slate-700'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setCurrentPage('analysis')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                currentPage === 'analysis'
                  ? darkMode ? 'bg-blue-600 text-white' : 'bg-blue-500 text-white'
                  : darkMode ? 'hover:bg-slate-700 text-gray-300' : 'hover:bg-gray-100 text-slate-700'
              }`}
            >
              Analysis
            </button>
          </div>
          <Button
            variant="outline"
            size="icon"
            onClick={() => setDarkMode(!darkMode)}
            className={darkMode ? 'border-blue-400 text-blue-400 hover:bg-blue-900/30' : 'border-blue-600 text-blue-600 hover:bg-blue-50'}
          >
            {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </Button>
        </div>
      </nav>
      
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className={`text-4xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
            MedParse - Multi-Organ AI Platform
          </h1>
          <p className={`text-lg mt-2 ${darkMode ? 'text-blue-300' : 'text-blue-600'}`}>
            Powered by Azure AI Foundry and Microsoft Healthcare AI Models
          </p>
          <p className={`text-sm mt-1 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
            Mode: {useMockData ? 'Demo (Mock Data)' : 'Production (Azure AI)'}
          </p>
        </div>

        <Alert className={`mb-6 ${darkMode ? 'bg-blue-900/30 border-blue-500' : 'bg-blue-50 border-blue-300'}`}>
          <Brain className={`h-4 w-4 ${darkMode ? 'text-blue-400' : 'text-blue-600'}`} />
          <AlertDescription className={darkMode ? 'text-blue-200' : 'text-blue-800'}>
            This healthcare AI platform is for research and demonstration purposes only. 
            Not intended for clinical use without proper regulatory approval.
          </AlertDescription>
        </Alert>

        {/* Organ Selector Tabs */}
        <Tabs value={selectedOrgan} onValueChange={(value) => setSelectedOrgan(value as 'liver' | 'hip')} className="mb-6">
          <TabsList className={`grid w-full grid-cols-2 ${darkMode ? 'bg-slate-800' : 'bg-slate-100'}`}>
            <TabsTrigger value="liver" className={darkMode ? 'data-[state=active]:bg-blue-900' : ''}>
              Liver Disease Analysis
            </TabsTrigger>
            <TabsTrigger value="hip" className={darkMode ? 'data-[state=active]:bg-blue-900' : ''}>
              Hip Replacement Planning
            </TabsTrigger>
          </TabsList>

          <TabsContent value="liver" className="mt-6">
            {/* Existing Liver Content */}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-8">
          {modalities.map((modality) => (
            <Card
              key={modality.id}
              className={`cursor-pointer transition-all ${
                selectedModality === modality.id
                  ? darkMode
                    ? 'bg-blue-900/50 border-blue-500 shadow-lg shadow-blue-500/50'
                    : 'bg-blue-100 border-blue-500 shadow-lg'
                  : darkMode
                  ? 'bg-slate-800/50 border-slate-700 hover:bg-slate-800/80'
                  : 'bg-white border-slate-200 hover:bg-slate-50'
              }`}
              onClick={() => setSelectedModality(modality.id)}
            >
              <CardHeader className="text-center pb-4">
                <modality.icon className={`h-8 w-8 mx-auto mb-2 ${
                  selectedModality === modality.id
                    ? darkMode ? 'text-blue-400' : 'text-blue-600'
                    : darkMode ? 'text-gray-400' : 'text-slate-600'
                }`} />
                <CardTitle className={`text-lg ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                  {modality.name}
                </CardTitle>
              </CardHeader>
            </Card>
          ))}
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className={`grid w-full grid-cols-4 ${darkMode ? 'bg-slate-800' : 'bg-slate-100'}`}>
            <TabsTrigger value="upload" className={darkMode ? 'data-[state=active]:bg-blue-900' : ''}>
              Upload Image
            </TabsTrigger>
            <TabsTrigger value="analyze" className={darkMode ? 'data-[state=active]:bg-blue-900' : ''} disabled={!uploadedImage}>
              Analyze
            </TabsTrigger>
            <TabsTrigger value="results" className={darkMode ? 'data-[state=active]:bg-blue-900' : ''} disabled={!results}>
              Results
            </TabsTrigger>
            <TabsTrigger value="batch" className={darkMode ? 'data-[state=active]:bg-blue-900' : ''}>
              Batch Processing
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upload" className="mt-6">
            <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
              <CardHeader>
                <CardTitle className={darkMode ? 'text-white' : 'text-slate-900'}>
                  Upload Liver Imaging or Select Patient
                </CardTitle>
                <CardDescription className={darkMode ? 'text-gray-400' : 'text-slate-600'}>
                  Upload a {selectedModality.replace('-', ' ').toUpperCase()} image or select a patient by ID
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {patients.length > 0 && (
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-slate-700'}`}>
                      Select Patient by ID
                    </label>
                    <select
                      value={selectedPatient}
                      onChange={(e) => {
                        setSelectedPatient(e.target.value)
                        if (e.target.value) {
                          loadDemoImage()
                        }
                      }}
                      className={`w-full px-4 py-2 rounded-lg border ${
                        darkMode 
                          ? 'bg-slate-900 border-slate-700 text-white' 
                          : 'bg-white border-slate-300 text-slate-900'
                      }`}
                    >
                      <option value="">-- Select a patient --</option>
                      {patients.map(patient => (
                        <option key={patient.id} value={patient.id}>
                          {patient.label} ({patient.id})
                        </option>
                      ))}
                    </select>
                  </div>
                )}
                <div className="text-center">
                  <p className={`mb-3 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>or</p>
                </div>
                <div
                  className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
                    darkMode
                      ? 'border-blue-500 bg-slate-900/50 hover:bg-slate-900/80 hover:border-blue-400'
                      : 'border-blue-300 bg-blue-50 hover:bg-blue-100 hover:border-blue-400'
                  }`}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className={`h-12 w-12 mx-auto mb-4 ${darkMode ? 'text-blue-400' : 'text-blue-600'}`} />
                  <p className={`text-lg font-semibold mb-2 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                    Click to upload or drag and drop
                  </p>
                  <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                    PNG, JPG, DICOM up to 50MB
                  </p>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                  />
                </div>

                <div className="text-center">
                  <p className={`mb-3 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>or</p>
                  <Button
                    onClick={loadDemoImage}
                    variant="outline"
                    className={darkMode ? 'border-blue-400 text-blue-400 hover:bg-blue-900/30' : 'border-blue-600 text-blue-600'}
                  >
                    <FileImage className="h-4 w-4 mr-2" />
                    Load Demo {selectedModality.toUpperCase()} Image
                  </Button>
                </div>

                {safeUploadedImage && (
                  <div className={`mt-6 p-4 rounded-xl ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                    <img
                      src={safeUploadedImage}
                      alt="Uploaded medical image"
                      className="max-w-full h-auto rounded-lg mx-auto"
                      style={{ maxHeight: '400px' }}
                    />
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analyze" className="mt-6">
            <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
              <CardHeader>
                <CardTitle className={darkMode ? 'text-white' : 'text-slate-900'}>
                  Liver Disease Analysis Pipeline
                </CardTitle>
                <CardDescription className={darkMode ? 'text-gray-400' : 'text-slate-600'}>
                  AI-powered hepatology analysis using Azure AI Foundry
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {safeUploadedImage && (
                  <div className={`p-4 rounded-xl ${darkMode ? 'bg-slate-900/50' : 'bg-slate-50'}`}>
                    <img
                      src={safeUploadedImage}
                      alt="Image to analyze"
                      className="max-w-full h-auto rounded-lg mx-auto"
                      style={{ maxHeight: '300px' }}
                    />
                  </div>
                )}

                <div className="space-y-4">
                  {analysisSteps.map((step, idx) => (
                    <div key={idx} className="flex items-center gap-4">
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                        step.status === 'complete'
                          ? darkMode ? 'bg-green-900/50 text-green-400' : 'bg-green-100 text-green-600'
                          : processing && analysisStep === idx
                          ? darkMode ? 'bg-blue-900/50 text-blue-400' : 'bg-blue-100 text-blue-600'
                          : darkMode ? 'bg-slate-700 text-gray-400' : 'bg-slate-200 text-slate-400'
                      }`}>
                        {step.status === 'complete' ? (
                          <CheckCircle2 className="h-5 w-5" />
                        ) : processing && analysisStep === idx ? (
                          <Loader2 className="h-5 w-5 animate-spin" />
                        ) : (
                          <span>{idx + 1}</span>
                        )}
                      </div>
                      <div className="flex-1">
                        <div className={`font-medium ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                          {step.name}
                        </div>
                        {processing && analysisStep === idx && (
                          <Progress value={66} className="mt-2 h-2" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                <Button
                  onClick={runAnalysis}
                  disabled={processing || !uploadedImage}
                  className={`w-full ${darkMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-600 hover:bg-blue-700'}`}
                  size="lg"
                >
                  {processing ? (
                    <>
                      <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Brain className="h-5 w-5 mr-2" />
                      Start AI Analysis
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="results" className="mt-6">
            {processing && !results && (
              <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
                <CardContent className="py-12">
                  <div className="flex flex-col items-center justify-center space-y-6">
                    <div className="relative">
                      <Loader2 className={`h-16 w-16 animate-spin ${darkMode ? 'text-blue-400' : 'text-blue-600'}`} />
                      <div className="absolute inset-0 rounded-full bg-blue-500/20 animate-ping" />
                    </div>
                    <div className="text-center space-y-2">
                      <h3 className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                        Processing Liver Scan
                      </h3>
                      <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                        {analysisStep === 1 && 'Running MedImageParse3D segmentation analysis...'}
                        {analysisStep === 2 && 'Generating GPT-4.1 initial clinical analysis...'}
                        {analysisStep === 0 && 'Initializing AI models...'}
                      </p>
                    </div>
                    <div className="w-full max-w-md">
                      <Progress value={(analysisStep / 3) * 100} className="h-2" />
                      <p className={`text-xs text-center mt-2 ${darkMode ? 'text-gray-500' : 'text-slate-500'}`}>
                        Step {analysisStep} of 3
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {results && (
              <div className="space-y-6">
                <Card className={darkMode ? 'bg-gradient-to-br from-blue-900/30 to-slate-800/50 border-blue-500/30' : 'bg-gradient-to-br from-blue-50 to-white border-blue-200'}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className={`text-2xl ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                          ✓ Analysis Complete
                        </CardTitle>
                        <CardDescription className={darkMode ? 'text-gray-400' : 'text-slate-600'}>
                          AI-powered liver disease assessment results
                        </CardDescription>
                      </div>
                      <CheckCircle2 className={`h-12 w-12 ${darkMode ? 'text-green-400' : 'text-green-600'}`} />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-3 gap-4">
                      <div className={`${darkMode ? 'bg-blue-900/40' : 'bg-blue-100'} p-6 rounded-xl border ${darkMode ? 'border-blue-500/30' : 'border-blue-200'}`}>
                        <div className={`text-3xl font-bold mb-1 ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>
                          {results.metrics.processingTime}
                        </div>
                        <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                          Processing Time
                        </div>
                      </div>
                      <div className={`${darkMode ? 'bg-green-900/40' : 'bg-green-100'} p-6 rounded-xl border ${darkMode ? 'border-green-500/30' : 'border-green-200'}`}>
                        <div className={`text-3xl font-bold mb-1 ${darkMode ? 'text-green-400' : 'text-green-600'}`}>
                          {results.metrics.accuracy}
                        </div>
                        <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                          Accuracy Score
                        </div>
                      </div>
                      <div className={`${darkMode ? 'bg-purple-900/40' : 'bg-purple-100'} p-6 rounded-xl border ${darkMode ? 'border-purple-500/30' : 'border-purple-200'}`}>
                        <div className={`text-3xl font-bold mb-1 ${darkMode ? 'text-purple-400' : 'text-purple-600'}`}>
                          {results.metrics.modelsUsed}
                        </div>
                        <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                          AI Models Used
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {uploadedImage && (
                  <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
                    <CardHeader>
                      <CardTitle className={darkMode ? 'text-white' : 'text-slate-900'}>
                        3D Liver Visualization
                      </CardTitle>
                      <CardDescription className={darkMode ? 'text-gray-400' : 'text-slate-600'}>
                        Interactive 3D rendering of liver anatomy
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <Liver3DViewer 
                        imageUrl={safeUploadedImage!} 
                        overlayUrl={results.overlayImageUrl}
                        darkMode={darkMode} 
                      />
                    </CardContent>
                  </Card>
                )}

                {results.demographics && (
                  <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
                    <CardHeader>
                      <CardTitle className={darkMode ? 'text-white' : 'text-slate-900'}>
                        Patient Demographics
                      </CardTitle>
                      <CardDescription className={darkMode ? 'text-gray-400' : 'text-slate-600'}>
                        Clinical study metadata from Kaggle liver disease dataset
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                        <DemoField 
                          label="Patient ID" 
                          value={results.demographics.patient_id} 
                          darkMode={darkMode} 
                        />
                        <DemoField 
                          label="Age" 
                          value={`${results.demographics.age} years`} 
                          darkMode={darkMode} 
                        />
                        <DemoField 
                          label="Gender" 
                          value={results.demographics.gender} 
                          darkMode={darkMode} 
                        />
                        <DemoField 
                          label="Ethnicity" 
                          value={results.demographics.ethnicity} 
                          darkMode={darkMode} 
                        />
                      </div>
                    </CardContent>
                  </Card>
                )}

                <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
                  <CardHeader>
                    <CardTitle className={`flex items-center gap-2 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                      <Microscope className="w-5 h-5" />
                      Liver Feature Classification
                    </CardTitle>
                    <CardDescription className={darkMode ? 'text-gray-400' : 'text-slate-600'}>
                      MedImageParse3D feature detection results
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className={`p-4 rounded-lg mb-4 ${darkMode ? 'bg-blue-900/20 border border-blue-500/30' : 'bg-blue-50 border border-blue-200'}`}>
                      <div className={`text-lg font-bold mb-2 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                        {results.embeddings.classification}
                      </div>
                    </div>
                    <div className={`space-y-2 ${darkMode ? 'text-gray-300' : 'text-slate-700'}`}>
                      {results.embeddings.features.map((feature, idx) => (
                        <div key={idx} className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${darkMode ? 'bg-blue-400' : 'bg-blue-600'}`} />
                          <span>{feature}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
                  <CardHeader>
                    <CardTitle className={`flex items-center gap-2 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                      <Activity className="w-5 h-5" />
                      Liver Tumor Segmentation
                    </CardTitle>
                    <CardDescription className={darkMode ? 'text-gray-400' : 'text-slate-600'}>
                      3D volumetric segmentation analysis
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {results.segmentation.detected.map((item, idx) => (
                        <div key={idx} className={`flex items-center justify-between p-3 rounded-lg ${
                          darkMode ? 'bg-slate-900/50 border border-slate-700' : 'bg-slate-50 border border-slate-200'
                        }`}>
                          <span className={`flex items-center gap-2 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                            <div className={`w-2 h-2 rounded-full ${darkMode ? 'bg-green-400' : 'bg-green-600'}`} />
                            {item}
                          </span>
                          <span className={`text-xs px-3 py-1 rounded-full font-medium ${
                            darkMode ? 'bg-green-900/50 text-green-400 border border-green-500/30' : 'bg-green-100 text-green-700 border border-green-200'
                          }`}>
                            Detected
                          </span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
                  <CardHeader>
                    <CardTitle className={`flex items-center gap-2 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                      <Brain className="w-5 h-5" />
                      Two-Stage Clinical Analysis
                    </CardTitle>
                    <CardDescription className={darkMode ? 'text-gray-400' : 'text-slate-600'}>
                      GPT-4.1 Clinical Analysis
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className={`prose max-w-none ${darkMode ? 'prose-invert' : ''}`}>
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          h1: ({node, ...props}) => <h1 className={`text-xl font-bold mb-3 mt-4 ${darkMode ? 'text-white' : 'text-slate-900'}`} {...props} />,
                          h2: ({node, ...props}) => <h2 className={`text-lg font-bold mb-2 mt-3 ${darkMode ? 'text-white' : 'text-slate-900'}`} {...props} />,
                          h3: ({node, ...props}) => <h3 className={`text-base font-semibold mb-2 mt-2 ${darkMode ? 'text-gray-200' : 'text-slate-800'}`} {...props} />,
                          h4: ({node, ...props}) => <h4 className={`text-sm font-semibold mb-1 mt-2 ${darkMode ? 'text-gray-200' : 'text-slate-800'}`} {...props} />,
                          p: ({node, ...props}) => <p className={`mb-3 last:mb-0 ${darkMode ? 'text-gray-300' : 'text-slate-700'}`} {...props} />,
                          ul: ({node, ...props}) => <ul className={`list-disc list-inside mb-3 space-y-1 ${darkMode ? 'text-gray-300' : 'text-slate-700'}`} {...props} />,
                          ol: ({node, ...props}) => <ol className={`list-decimal list-inside mb-3 space-y-1 ${darkMode ? 'text-gray-300' : 'text-slate-700'}`} {...props} />,
                          li: ({node, ...props}) => <li className={`ml-2 ${darkMode ? 'text-gray-300' : 'text-slate-700'}`} {...props} />,
                          strong: ({node, ...props}) => <strong className={`font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`} {...props} />,
                          em: ({node, ...props}) => <em className={`italic ${darkMode ? 'text-gray-300' : 'text-slate-700'}`} {...props} />,
                          code: ({node, ...props}) => <code className={`px-1 py-0.5 rounded text-xs ${darkMode ? 'bg-slate-800 text-blue-300' : 'bg-slate-200 text-blue-700'}`} {...props} />,
                          blockquote: ({node, ...props}) => <blockquote className={`border-l-4 pl-4 italic my-3 ${darkMode ? 'border-blue-500 text-gray-400' : 'border-blue-300 text-slate-600'}`} {...props} />,
                        }}
                      >
                        {results.gpt5Analysis}
                      </ReactMarkdown>
                    </div>
                  </CardContent>
                </Card>

                <Card className={darkMode ? 'bg-gradient-to-br from-slate-800/50 to-blue-900/30 border-blue-500/30' : 'bg-gradient-to-br from-white to-blue-50 border-blue-200'}>
                  <CardContent className="py-6">
                    <div className="grid grid-cols-4 gap-6">
                      {[
                        { label: 'Models Used', value: 'MedImageParse3D, GPT-4.1', icon: Brain },
                        { label: 'Confidence Score', value: results.metrics.accuracy, icon: CheckCircle2 },
                        { label: 'Processing Method', value: useMockData ? 'Demo Mode' : 'Azure AI Foundry', icon: Zap },
                        { label: 'Compliance', value: 'Research Use Only', icon: Activity }
                      ].map((stat, idx) => (
                        <div key={idx} className="text-center space-y-2">
                          <stat.icon className={`h-6 w-6 mx-auto ${darkMode ? 'text-blue-400' : 'text-blue-600'}`} />
                          <div className={`text-sm font-medium ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                            {stat.label}
                          </div>
                          <div className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                            {stat.value}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>

          <TabsContent value="batch" className="mt-6">
            <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
              <CardHeader>
                <CardTitle className={darkMode ? 'text-white' : 'text-slate-900'}>
                  Batch Processing
                </CardTitle>
                <CardDescription className={darkMode ? 'text-gray-400' : 'text-slate-600'}>
                  Analyze up to 20 patients serially with comprehensive results dashboard
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {patients.length > 0 && (
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-slate-700'}`}>
                      Select Patients for Batch Analysis (Hold Ctrl/Cmd for multiple)
                    </label>
                    <select
                      multiple
                      value={batchPatients}
                      onChange={(e) => {
                        const selected = Array.from(e.target.selectedOptions, option => option.value)
                        if (selected.length <= 20) {
                          setBatchPatients(selected)
                        } else {
                          alert('Maximum 20 patients per batch')
                        }
                      }}
                      className={`w-full px-4 py-2 rounded-lg border h-64 ${
                        darkMode 
                          ? 'bg-slate-900 border-slate-700 text-white' 
                          : 'bg-white border-slate-300 text-slate-900'
                      }`}
                    >
                      {patients.map(patient => (
                        <option key={patient.id} value={patient.id}>
                          {patient.label} ({patient.id})
                        </option>
                      ))}
                    </select>
                    <p className={`text-sm mt-2 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                      {batchPatients.length} patient(s) selected
                    </p>
                  </div>
                )}

                <Button
                  onClick={async () => {
                    if (batchPatients.length === 0) {
                      alert('Please select at least one patient')
                      return
                    }
                    
                    setBatchProcessing(true)
                    setBatchResults([])
                    
                    try {
                      const formData = new FormData()
                      formData.append('patient_ids', batchPatients.join(','))
                      formData.append('modality', selectedModality)
                      
                      const response = await fetch(`${API_URL}/api/analyze/batch`, {
                        method: 'POST',
                        body: formData
                      })
                      
                      if (!response.ok) {
                        throw new Error('Batch analysis failed')
                      }
                      
                      const result = await response.json()
                      if (result.success) {
                        setBatchResults(result.results)
                      }
                    } catch (error) {
                      console.error('Batch processing error:', error)
                      alert('Batch processing failed. Please try again.')
                    } finally {
                      setBatchProcessing(false)
                    }
                  }}
                  disabled={batchProcessing || batchPatients.length === 0}
                  className={`w-full ${darkMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-600 hover:bg-blue-700'}`}
                  size="lg"
                >
                  {batchProcessing ? (
                    <>
                      <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                      Processing {batchPatients.length} Patients...
                    </>
                  ) : (
                    <>
                      <Brain className="h-5 w-5 mr-2" />
                      Start Batch Analysis
                    </>
                  )}
                </Button>

                {batchResults.length > 0 && (
                  <div className="mt-8 space-y-6">
                    <div className="grid grid-cols-3 gap-4">
                      <div className={`${darkMode ? 'bg-blue-900/40' : 'bg-blue-100'} p-4 rounded-xl`}>
                        <div className={`text-2xl font-bold ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>
                          {batchResults.length}
                        </div>
                        <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                          Total Processed
                        </div>
                      </div>
                      <div className={`${darkMode ? 'bg-green-900/40' : 'bg-green-100'} p-4 rounded-xl`}>
                        <div className={`text-2xl font-bold ${darkMode ? 'text-green-400' : 'text-green-600'}`}>
                          {batchResults.filter(r => r.success).length}
                        </div>
                        <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                          Successful
                        </div>
                      </div>
                      <div className={`${darkMode ? 'bg-red-900/40' : 'bg-red-100'} p-4 rounded-xl`}>
                        <div className={`text-2xl font-bold ${darkMode ? 'text-red-400' : 'text-red-600'}`}>
                          {batchResults.filter(r => !r.success).length}
                        </div>
                        <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                          Failed
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      {batchResults.map((result, idx) => (
                        <Card key={idx} className={darkMode ? 'bg-slate-900/50 border-slate-700' : 'bg-white border-slate-200'}>
                          <CardHeader>
                            <CardTitle className={`text-sm flex items-center justify-between ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                              <span>{result.patient_id}</span>
                              {result.success ? (
                                <CheckCircle2 className="h-4 w-4 text-green-500" />
                              ) : (
                                <span className="text-red-500 text-xs">Failed</span>
                              )}
                            </CardTitle>
                          </CardHeader>
                          {result.success && result.data && (
                            <CardContent className="space-y-2">
                              <div className="grid grid-cols-2 gap-2">
                                <div>
                                  <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                                    Original
                                  </p>
                                  <img
                                    src={safeUploadedImage || ''}
                                    alt="Original"
                                    className="w-full h-32 object-cover rounded"
                                  />
                                </div>
                                <div>
                                  <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                                    Segmented
                                  </p>
                                  <img
                                    src={result.data.overlayImageUrl || safeUploadedImage || ''}
                                    alt="Segmented"
                                    className="w-full h-32 object-cover rounded"
                                  />
                                </div>
                              </div>
                              <div className={`text-xs ${darkMode ? 'text-gray-300' : 'text-slate-700'}`}>
                                <p><strong>Classification:</strong> {result.data.embeddings.classification}</p>
                                <p><strong>Accuracy:</strong> {result.data.metrics.accuracy}</p>
                              </div>
                            </CardContent>
                          )}
                          {!result.success && (
                            <CardContent>
                              <p className={`text-xs ${darkMode ? 'text-red-400' : 'text-red-600'}`}>
                                {result.error}
                              </p>
                            </CardContent>
                          )}
                        </Card>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
          </TabsContent>

          <TabsContent value="hip" className="mt-6">
            <HipDemo darkMode={darkMode} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App
