import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Clock, Target, CheckCircle, Zap, CheckCircle2, Activity, Settings, Ruler } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface HipAnalysisResult {
  segmentation: {
    detected: string[]
    quality: string
    femur_accuracy?: number
    pelvis_accuracy?: number
    acetabulum_accuracy?: number
  }
  implantSizing: Record<string, string>
  alignmentMetrics: Record<string, string>
  surgicalPlan: string
  gpt41Analysis?: string
  demographics?: {
    patient_id: string
    age: number
    gender: string
    bmi?: number
    medical_history?: string
  }
  metrics: {
    processingTime: string
    accuracy: string
    bonesSegmented: number
  }
}

export default function HipDemo({ darkMode }: { darkMode: boolean }) {
  const [selectedPatient, setSelectedPatient] = useState('')
  const [patients, setPatients] = useState<Array<{id: string, label: string}>>([])
  const [results, setResults] = useState<HipAnalysisResult | null>(null)
  const [processing, setProcessing] = useState(false)
  const [segmentationComplete, setSegmentationComplete] = useState(false)
  const [ctImages, setCtImages] = useState<Record<string, string>>({})

  useEffect(() => {
    fetch(`${API_URL}/api/hip/demo-data`)
      .then(res => res.json())
      .then(data => {
        setResults(data)
        setSegmentationComplete(true)
      })
      .catch(err => console.error('Demo data load error:', err))
    
    fetch(`${API_URL}/api/hip/patients`)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setPatients(data.patients)
        }
      })
      .catch(err => console.error('Patients fetch error:', err))
    
    fetch(`${API_URL}/api/hip/ct-images`)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setCtImages(data.images)
        }
      })
      .catch(err => console.error('CT images load error:', err))
  }, [])

  const handleAnalyze = async () => {
    if (!selectedPatient) return
    
    setProcessing(true)
    setSegmentationComplete(false)
    
    try {
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const formData = new FormData()
      formData.append('patient_id', selectedPatient)
      
      const response = await fetch(`${API_URL}/api/hip/analyze`, {
        method: 'POST',
        body: formData
      })
      
      const result = await response.json()
      if (result.success) {
        setResults(result.data)
        setSegmentationComplete(true)
      }
    } catch (error) {
      console.error('Hip analysis error:', error)
    } finally {
      setProcessing(false)
    }
  }

  return (
    <div className={`space-y-6 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
      {/* Header */}
      <div>
        <div className="flex justify-between items-start">
          <div>
            <h1 className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              HipMedParse
            </h1>
            <p className={`text-base mt-1 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
              AI-Powered Hip Segmentation for Robotic Surgery Planning
            </p>
            <p className={`text-sm mt-1 ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>
              Built on MedImageParse3D Foundation Model
            </p>
          </div>
          <div className="text-right">
            <p className={`font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>Greg Katz</p>
            <a href="https://github.com/gregnatkatz" className={`text-sm ${darkMode ? 'text-blue-400' : 'text-blue-600'} hover:underline`}>
              github.com/gregnatkatz
            </a>
          </div>
        </div>
      </div>

      {/* Metrics Cards Row */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard
          title="Processing Time"
          value={results?.metrics.processingTime || "3.8min"}
          subtitle="vs 128 min manual"
          icon={Clock}
          darkMode={darkMode}
          iconColor="text-green-500"
        />
        <MetricCard
          title="Accuracy"
          value={results?.metrics.accuracy || "96.2%"}
          subtitle="Dice coefficient"
          icon={Target}
          darkMode={darkMode}
          iconColor="text-blue-500"
        />
        <MetricCard
          title="Bones Segmented"
          value={String(results?.metrics.bonesSegmented || 4)}
          subtitle="Femur, Tibia, Fibula, Patella"
          icon={CheckCircle}
          darkMode={darkMode}
          iconColor="text-purple-500"
        />
        <MetricCard
          title="Component Size"
          value="92%"
          subtitle="Sizing accuracy"
          icon={Zap}
          darkMode={darkMode}
          iconColor="text-orange-500"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left Column - CT Upload and Status */}
        <div className="space-y-4">
          <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
            <CardHeader>
              <CardTitle className={darkMode ? 'text-white' : 'text-slate-900'}>
                CT Upload
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <select
                value={selectedPatient}
                onChange={(e) => setSelectedPatient(e.target.value)}
                className={`w-full px-4 py-2 rounded-lg border ${
                  darkMode 
                    ? 'bg-slate-900 border-slate-700 text-white' 
                    : 'bg-white border-slate-300 text-slate-900'
                }`}
              >
                <option value="">-- Select a patient --</option>
                {patients.map(patient => (
                  <option key={patient.id} value={patient.id}>
                    {patient.label}
                  </option>
                ))}
              </select>
              
              <Button
                onClick={handleAnalyze}
                disabled={!selectedPatient || processing}
                className="w-full"
              >
                {processing ? 'Analyzing...' : 'Start Analysis'}
              </Button>

              {segmentationComplete && (
                <Alert className={`${darkMode ? 'bg-green-900/30 border-green-600' : 'bg-green-50 border-green-400'}`}>
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <AlertDescription className={darkMode ? 'text-green-300' : 'text-green-800'}>
                    <strong>Segmentation Complete</strong>
                    <p className="text-sm mt-1">
                      {results?.segmentation.detected.length} bones identified and segmented successfully
                    </p>
                  </AlertDescription>
                </Alert>
              )}

              {/* Segmented Structures */}
              {results && (
                <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
                  <CardHeader>
                    <CardTitle className={`flex items-center gap-2 text-sm ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                      <Activity className="w-4 h-4" />
                      Segmented Bone Structures
                    </CardTitle>
                    <p className={`text-xs mt-1 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                      MedImageParse3D 3D volumetric segmentation
                    </p>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {results.segmentation.detected.map((bone, idx) => {
                        const accuracies: Record<string, number | undefined> = {
                          'Femur': results.segmentation.femur_accuracy,
                          'Pelvis': results.segmentation.pelvis_accuracy,
                          'Acetabulum': results.segmentation.acetabulum_accuracy
                        }
                        const accuracy = accuracies[bone]
                        
                        return (
                          <div key={idx} className={`flex items-center justify-between p-3 rounded-lg ${
                            darkMode ? 'bg-slate-900/50 border border-slate-700' : 'bg-slate-50 border border-slate-200'
                          }`}>
                            <span className={`flex items-center gap-2 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                              <div className={`w-2 h-2 rounded-full ${darkMode ? 'bg-green-400' : 'bg-green-600'}`} />
                              {bone}
                            </span>
                            {accuracy && (
                              <span className={`text-xs px-3 py-1 rounded-full font-medium ${
                                accuracy >= 96 
                                  ? (darkMode ? 'bg-green-900/50 text-green-400 border border-green-500/30' : 'bg-green-100 text-green-700 border border-green-200')
                                  : (darkMode ? 'bg-blue-900/50 text-blue-400 border border-blue-500/30' : 'bg-blue-100 text-blue-700 border border-blue-200')
                              }`}>
                                {accuracy.toFixed(1)}%
                              </span>
                            )}
                          </div>
                        )
                      })}
                    </div>
                  </CardContent>
                </Card>
              )}

              <Button
                variant="outline"
                className="w-full"
                onClick={() => {
                  setSegmentationComplete(false)
                  setResults(null)
                  setSelectedPatient('')
                }}
              >
                Reset Analysis
              </Button>

              {/* Compatibility Badges */}
              <div className="pt-4 border-t border-slate-700">
                <p className={`text-sm font-semibold mb-2 ${darkMode ? 'text-gray-300' : 'text-slate-700'}`}>
                  Compatible With:
                </p>
                <div className="space-y-1 text-sm">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                    <span className={darkMode ? 'text-gray-400' : 'text-slate-600'}>ABC MedTech Robotic System</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                    <span className={darkMode ? 'text-gray-400' : 'text-slate-600'}>Major Surgical Platforms</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                    <span className={darkMode ? 'text-gray-400' : 'text-slate-600'}>DICOM-Compatible Systems</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column - 3D Segmentation View and Results */}
        <div className="col-span-2 space-y-4">
          {/* 3D Segmentation View */}
          <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle className={darkMode ? 'text-white' : 'text-slate-900'}>
                  3D Segmentation View
                </CardTitle>
                <div className="flex gap-2">
                  <button className="px-3 py-1 text-sm rounded bg-slate-700 text-white">Axial</button>
                  <button className="px-3 py-1 text-sm rounded bg-blue-600 text-white">3D</button>
                  <button className="px-3 py-1 text-sm rounded bg-slate-700 text-white">Sagittal</button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* 6-Panel Bone Registration View with Red Contrast Overlays */}
              <div className={`rounded-lg p-4 ${darkMode ? 'bg-slate-900' : 'bg-slate-100'}`}>
                <div className="grid grid-cols-3 grid-rows-2 gap-2">
                  {[
                    { title: 'Axial View', view: 'axial' },
                    { title: 'Coronal View', view: 'coronal' },
                    { title: 'Sagittal View', view: 'sagittal' },
                    { title: '3D Anterior', view: '3d_anterior' },
                    { title: '3D Lateral', view: '3d_lateral' },
                    { title: '3D Superior', view: '3d_superior' }
                  ].map((panel, idx) => (
                    <div key={idx} className={`aspect-square rounded-lg border-2 ${
                      darkMode ? 'border-red-500/50 bg-slate-800' : 'border-red-300 bg-white'
                    } p-2 flex flex-col`}>
                      <p className={`text-xs font-semibold mb-1 ${darkMode ? 'text-gray-300' : 'text-slate-700'}`}>
                        {panel.title}
                      </p>
                      <div className={`flex-1 flex items-center justify-center ${
                        darkMode ? 'bg-slate-700/50' : 'bg-slate-200/50'
                      } rounded overflow-hidden`}>
                        {ctImages[panel.view] ? (
                          <img 
                            src={ctImages[panel.view]} 
                            alt={panel.title}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-16 h-16 bg-red-500 rounded opacity-60 animate-pulse"></div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-3 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-4">
                    <span className={`flex items-center gap-1 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                      <span className="w-3 h-3 bg-gray-400 rounded"></span> CT Scan
                    </span>
                    <span className={`flex items-center gap-1 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                      <span className="w-3 h-3 bg-red-500 rounded"></span> Bone Segmentation
                    </span>
                  </div>
                  <div className={`${darkMode ? 'text-red-400' : 'text-red-600'} font-semibold`}>
                    ✓ AI Bone Segmentation with Red Contrast
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Implant Sizing and Alignment Grid */}
          {results && (
            <div className="grid grid-cols-2 gap-4">
              <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
                <CardHeader>
                  <CardTitle className={`flex items-center gap-2 text-base ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                    <Settings className="w-4 h-4" />
                    Implant Sizing
                  </CardTitle>
                  <p className={`text-xs mt-1 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                    AI-recommended component sizes
                  </p>
                </CardHeader>
                <CardContent className="space-y-3">
                  {Object.entries(results.implantSizing).map(([key, value]) => (
                    <div key={key} className={`p-3 rounded-lg ${
                      darkMode ? 'bg-blue-900/20 border border-blue-500/30' : 'bg-blue-50 border border-blue-200'
                    }`}>
                      <div className={`text-xs mb-1 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                        {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </div>
                      <div className={`text-base font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                        {value}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
                <CardHeader>
                  <CardTitle className={`flex items-center gap-2 text-base ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                    <Ruler className="w-4 h-4" />
                    Alignment Metrics
                  </CardTitle>
                  <p className={`text-xs mt-1 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                    Anatomical measurements
                  </p>
                </CardHeader>
                <CardContent className="space-y-3">
                  {Object.entries(results.alignmentMetrics).map(([key, value]) => (
                    <div key={key} className={`p-3 rounded-lg ${
                      darkMode ? 'bg-purple-900/20 border border-purple-500/30' : 'bg-purple-50 border border-purple-200'
                    }`}>
                      <div className={`text-xs mb-1 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                        {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </div>
                      <div className={`text-base font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                        {value}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          )}

          {/* Surgical Planning */}
          {results && (
            <Card className={darkMode ? 'bg-blue-900/20 border-blue-600' : 'bg-blue-50 border-blue-300'}>
              <CardHeader>
                <CardTitle className={`text-base ${darkMode ? 'text-blue-300' : 'text-blue-900'}`}>
                  <CheckCircle2 className="inline mr-2 h-5 w-5" />
                  Surgical Planning Complete
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className={`text-sm ${darkMode ? 'text-blue-200' : 'text-blue-800'}`}>
                  Ready to export to ABC MedTech robotic system for intraoperative guidance
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Patient Demographics and GPT-4.1 Analysis */}
      {results && results.demographics && (
        <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
          <CardHeader>
            <CardTitle className={darkMode ? 'text-white' : 'text-slate-900'}>
              Patient Demographics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div>
                <p className={`text-sm mb-1 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                  Patient ID
                </p>
                <p className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                  {results.demographics.patient_id}
                </p>
              </div>
              <div>
                <p className={`text-sm mb-1 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                  Age
                </p>
                <p className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                  {results.demographics.age} years
                </p>
              </div>
              <div>
                <p className={`text-sm mb-1 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                  Gender
                </p>
                <p className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                  {results.demographics.gender}
                </p>
              </div>
              {results.demographics.bmi && (
                <div>
                  <p className={`text-sm mb-1 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                    BMI
                  </p>
                  <p className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                    {results.demographics.bmi}
                  </p>
                </div>
              )}
            </div>
            {results.demographics.medical_history && (
              <div className="mt-4">
                <p className={`text-sm mb-1 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
                  Medical History
                </p>
                <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-slate-700'}`}>
                  {results.demographics.medical_history}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {results && results.gpt41Analysis && (
        <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
          <CardHeader>
            <CardTitle className={`flex items-center gap-2 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
              <CheckCircle2 className="w-5 h-5" />
              Comprehensive GPT-4.1 Clinical Analysis
            </CardTitle>
            <p className={`text-sm mt-1 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
              AI-powered surgical planning recommendations and risk assessment
            </p>
          </CardHeader>
          <CardContent>
            <div className={`prose max-w-none ${darkMode ? 'prose-invert' : ''} text-sm ${darkMode ? 'text-gray-300' : 'text-slate-700'}`}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {results.gpt41Analysis}
              </ReactMarkdown>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Bottom Info Sections */}
      {results && (
        <div className="grid grid-cols-3 gap-6">
          <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
            <CardHeader>
              <CardTitle className={`text-sm ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Technology
              </CardTitle>
            </CardHeader>
            <CardContent className={`text-xs ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
              Built on Microsoft's MedImageParse3D foundation model. Fine-tuned for orthopedic bone segmentation with CT imaging data.
            </CardContent>
          </Card>

          <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
            <CardHeader>
              <CardTitle className={`text-sm ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Performance
              </CardTitle>
            </CardHeader>
            <CardContent className={`text-xs ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
              Achieves 96%+ accuracy with 97% reduction in processing time compared to manual segmentation workflows.
            </CardContent>
          </Card>

          <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
            <CardHeader>
              <CardTitle className={`text-sm ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                Integration
              </CardTitle>
            </CardHeader>
            <CardContent className={`text-xs ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
              DICOM-compatible pipeline ready for integration with major robotic surgery platforms including ABC MedTech and other leading systems.
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

function MetricCard({ title, value, subtitle, icon: Icon, darkMode, iconColor }: any) {
  return (
    <Card className={darkMode ? 'bg-slate-800/50 border-slate-700' : 'bg-white border-slate-200'}>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between mb-2">
          <Icon className={`h-6 w-6 ${iconColor}`} />
        </div>
        <div className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
          {value}
        </div>
        <div className={`text-xs mt-1 ${darkMode ? 'text-gray-400' : 'text-slate-600'}`}>
          {title}
        </div>
        <div className={`text-xs mt-0.5 ${darkMode ? 'text-gray-500' : 'text-slate-500'}`}>
          {subtitle}
        </div>
      </CardContent>
    </Card>
  )
}

function getAccuracyColor(accuracy: number): string {
  if (accuracy >= 96) return 'text-blue-500'
  if (accuracy >= 95) return 'text-green-500'
  if (accuracy >= 90) return 'text-yellow-500'
  return 'text-orange-500'
}
