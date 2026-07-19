# 結構化輸出模板

## 1. 論文方法概覽表
| 欄位 | 內容 |
|---|---|
| 論文標題 | |
| 研究主題 | |
| 研究設計 | |
| 方法類型 | |
| 樣本與情境 | |
| 資料來源 | |
| 分析單位 | |
| 主要變數／構念 | |
| 主要分析方法 | |
| 主要品質檢查 | |
| 方法定位一句話 | |

## 2. JSON-style schema
```json
{
  "paper_metadata": {
    "title": "",
    "authors": "",
    "year": "",
    "journal_or_venue": ""
  },
  "research_question": {
    "research_objective": "",
    "hypotheses_or_propositions": [],
    "theoretical_logic_relevant_to_method_choice": ""
  },
  "study_design": {
    "design_type": "",
    "method_family": "",
    "time_structure": "",
    "setting": "",
    "unit_of_analysis": ""
  },
  "sample_and_data": {
    "sample_description": "",
    "sample_size": "",
    "sampling_method": "",
    "context": "",
    "data_source": "",
    "data_collection_procedure": "",
    "missing_data_handling": "",
    "exclusion_rules": ""
  },
  "measurement": {
    "key_constructs_or_variables": [],
    "operationalization": [],
    "scale_or_item_source": "",
    "reliability_evidence": [],
    "validity_evidence": [],
    "common_method_bias_checks": []
  },
  "analysis_pipeline": {
    "preprocessing": [],
    "descriptive_analysis": [],
    "measurement_model_testing": [],
    "main_model_estimation": [],
    "additional_tests": [],
    "robustness_checks": []
  },
  "estimation_and_testing": {
    "statistical_techniques": [],
    "estimation_method": "",
    "inference_criteria": "",
    "fit_indices_or_model_evaluation": [],
    "effect_size_reporting": "",
    "software_used": []
  },
  "identification_and_assumptions": {
    "causal_or_analytical_logic": "",
    "key_assumptions": [],
    "threats_to_validity_addressed": []
  },
  "method_contribution": {
    "method_level_difference_from_prior_work": [],
    "novelty_in_design_measurement_or_analysis": []
  },
  "quality_assessment": {
    "design_quality": "",
    "measurement_quality": "",
    "analysis_quality": "",
    "reporting_transparency": "",
    "major_methodological_strengths": [],
    "major_methodological_limitations": []
  },
  "comparison_ready_summary": {
    "one_sentence_method_summary": "",
    "comparison_tags": []
  },
  "evidence_and_confidence": {
    "direct_evidence_available": "",
    "unclear_or_not_reported_items": [],
    "inference_made_by_extractor": [],
    "overall_confidence": ""
  }
}
```

## 3. comparison-ready 表格
| 面向 | 抽取結果 |
|---|---|
| 研究目的 | |
| 研究設計 | |
| 方法類型 | |
| 樣本 | |
| 情境 | |
| 分析單位 | |
| 資料來源 | |
| 量測方式 | |
| 信度／效度 | |
| 主要統計方法 | |
| 分析流程 | |
| 推論／識別邏輯 | |
| 穩健性檢查 | |
| 方法創新點 | |
| 與既有研究差異 | |
| 方法限制 | |
