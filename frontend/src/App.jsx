import { useState } from 'react'
import useAnalysis from './hooks/useAnalysis'
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
  const analysis = useAnalysis()

  const calculate = () => {
    analysis.start(
      { portfolio: toRequestPortfolio(items), days: settings.days, horizon: settings.horizon, n_sim: settings.simulations },
      items,
    )
    setStep('analyse')
  }

  const generate = () => {
    if (analysis.report.status === 'idle') analysis.generateReport()
    setStep('report')
  }

  return (
    <>
      <TopBar step={step} enabled={{ build: true, analyse: analysis.request !== null, report: analysis.risk.status === 'ok' }} onStep={setStep} />
      {step === 'build' && (
        <BuildPage items={items} settings={settings} onItems={setItems} onSettings={setSettings} onCalculate={calculate} />
      )}
      {step === 'analyse' && <AnalysisPage analysis={analysis} onGenerate={generate} />}
      {step === 'report' && <ReportPage analysis={analysis} />}
    </>
  )
}
