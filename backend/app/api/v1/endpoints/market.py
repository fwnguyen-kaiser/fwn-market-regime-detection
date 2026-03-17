import logging
from fastapi import APIRouter, HTTPException
from app.services.data_service import DataService
from app.services.pipeline_service import PipelineService
from app.schemas.request import FetchRequest, AnalyzeRequest
from app.schemas.response import MessageResponse, AnalysisResponse
from app.engine.walk_forward import walk_forward_validation
from app.engine.features import HMMPreprocessor

# Initialize logger for this module
logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency Injection is recommended here, but simple instantiation works for now
data_service = DataService()
pipeline_service = PipelineService()

@router.post("/fetch", response_model=MessageResponse)
def fetch_market_data(req: FetchRequest):
    """
    Endpoint to fetch market data from external API (FMP) and save to local storage.
    Note: Using standard 'def' because underlying 'requests' library is synchronous.
    """
    logger.info(f"📥 [Fetch] Request received: Ticker={req.ticker}, Start={req.start_date}, End={req.end_date}")
    
    try:
        logger.info("🔄 Calling data_service.fetch_and_save...")
        # Assuming this method blocks (uses requests), so we run it in a thread (FastAPI default for non-async def)
        filename = data_service.fetch_and_save(req.ticker, req.start_date, req.end_date)
        
        logger.info(f"✅ [Fetch] Success! Data saved to: {filename}")
        
        # Return Pydantic model instance for better validation
        return MessageResponse(message="Data downloaded successfully", filename=filename)
    
    except Exception as e:
        # exc_info=True logs the full traceback automatically
        logger.error(f"❌ [Fetch] Error in endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/files")
def list_data_files():
    """
    List all available datasets in the storage directory.
    """
    try:
        files = data_service.list_datasets()
        logger.info(f"📂 [Files] Found {len(files)} datasets.")
        return {"files": files}
    except Exception as e:
        logger.error(f"❌ [Files] Error listing files: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not list files")

@router.post("/analyze", response_model=AnalysisResponse)
def analyze_regime(req: AnalyzeRequest):
    """
    Trigger the analysis pipeline (Hidden Markov Model) on a specific file.
    """
    logger.info(f"📊 [Analyze] Request received for file: {req.filename}")
    
    try:
        # Run the pipeline logic
        result = pipeline_service.run_analysis_on_file(req.filename)
        logger.info("✅ [Analyze] Analysis completed successfully.")
        return result
    
    except Exception as e:
        logger.error(f"❌ [Analyze] Error during analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/")
def market_root():
    return {"message": "Market router is alive"}
@router.post("/validate")
def validate_walk_forward(req: AnalyzeRequest):
    """
    Run walk-forward validation on a dataset.
    Returns BIC stability and regime distribution across folds.
    """
    try:
        df_raw = data_service.load_dataset(req.filename)
        # ⚠️ DO NOT truncate here — pass the full data
        prep_result = HMMPreprocessor.csv_to_features(df_raw)
        df = prep_result['df']
        feature_cols = prep_result['feature_cols']

        summary = walk_forward_validation(
            df=df,
            feature_cols=feature_cols,
            n_states=3,
            train_size=500,
            test_size=60,
            step_size=60,
            expanding=True,
        )
        return summary
    except Exception as e:
        logger.error(f"❌ Walk-forward error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))