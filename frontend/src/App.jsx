import { useState } from 'react'
import TopBar from './components/TopBar'
import { DEFAULT_SETTINGS } from './config'
import { toRequestPortfolio } from './lib/portfolio'
import AnalysisPage from './pages/AnalysisPage'
import BuildPage from './pages/BuildPage'
import ReportPage from './pages/ReportPage'

export default function App() {
  const [step, setStep] = useState('build')
  const [items, setItems] = useState([])
  const [settings, setSettings] = useState(DEFAULT_SETTINGS)
  const [request, setRequest] = useState(null)

  const calculate = () => {
    setRequest({ portfolio: toRequestPortfolio(items), days: settings.days, horizon: settings.horizon, n_sim: settings.simulations })
    setStep('analyse')
  }

  return (
    <>
      <TopBar step={step} enabled={{ build: true, analyse: request !== null, report: false }} onStep={setStep} />
      {step === 'build' && (
        <BuildPage items={items} settings={settings} onItems={setItems} onSettings={setSettings} onCalculate={calculate} />
      )}
      {step === 'analyse' && <AnalysisPage request={request} />}
      {step === 'report' && <ReportPage />}
    </>
  )
}
