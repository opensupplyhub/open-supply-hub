import logging
from typing import Dict, List, Set, Tuple
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import models
from django.core.exceptions import FieldDoesNotExist

logger = logging.getLogger(__name__)


class SyncVerifier:
    """Verifies sync status between OS Hub and RBA databases"""
    
    def __init__(self):
        self.models_with_uuid = self._get_models_with_uuid()
        self.sync_status: Dict[str, Dict] = {}
    
    def _get_models_with_uuid(self) -> List[models.Model]:
        """Get all models that have UUID fields and exist in both databases"""
        models_with_uuid = []
        
        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                try:
                    model._meta.get_field('uuid')
                    # Check if model exists in both databases
                    try:
                        model.objects.using('default').count()
                        model.objects.using('rba').count()
                        models_with_uuid.append(model)
                    except Exception as e:
                        logger.debug(f"Skipping {model._meta.app_label}.{model._meta.model_name}: {e}")
                except Exception:
                    continue
        
        return models_with_uuid
    
    def get_uuid_sets(self, model: models.Model) -> Tuple[Set[str], Set[str]]:
        """Get UUID sets from both databases for a model"""
        try:
            os_uuids = set(model.objects.using('default').values_list('uuid', flat=True))
            rba_uuids = set(model.objects.using('rba').values_list('uuid', flat=True))
            return os_uuids, rba_uuids
        except Exception as e:
            logger.error(f"Error getting UUIDs for {model._meta.app_label}.{model._meta.model_name}: {e}")
            return set(), set()
    
    def verify_model_sync(self, model: models.Model) -> Dict:
        """Verify sync status for a single model"""
        model_key = f"{model._meta.app_label}.{model._meta.model_name}"
        logger.info(f"Verifying sync for {model_key}")
        
        os_uuids, rba_uuids = self.get_uuid_sets(model)
        
        missing_in_rba = os_uuids - rba_uuids
        extra_in_rba = rba_uuids - os_uuids
        
        status = {
            'model_key': model_key,
            'os_count': len(os_uuids),
            'rba_count': len(rba_uuids),
            'missing_in_rba': len(missing_in_rba),
            'extra_in_rba': len(extra_in_rba),
            'missing_uuids': list(missing_in_rba)[:10],  # Show first 10 missing UUIDs
            'extra_uuids': list(extra_in_rba)[:10],      # Show first 10 extra UUIDs
            'is_synced': len(missing_in_rba) == 0 and len(extra_in_rba) == 0
        }
        
        if missing_in_rba:
            logger.warning(f"{model_key}: {len(missing_in_rba)} records missing in RBA")
        if extra_in_rba:
            logger.warning(f"{model_key}: {len(extra_in_rba)} extra records in RBA")
        if status['is_synced']:
            logger.info(f"{model_key}: ✓ Fully synced")
        
        return status
    
    def verify_all_models(self) -> Dict[str, Dict]:
        """Verify sync status for all models"""
        logger.info(f"Verifying sync for {len(self.models_with_uuid)} models")
        
        for model in self.models_with_uuid:
            status = self.verify_model_sync(model)
            self.sync_status[status['model_key']] = status
        
        return self.sync_status
    
    def get_missing_uuids_detailed(self, model: models.Model, limit: int = 50) -> List[str]:
        """Get detailed list of missing UUIDs for a model"""
        os_uuids, rba_uuids = self.get_uuid_sets(model)
        missing_uuids = list(os_uuids - rba_uuids)
        return missing_uuids[:limit]
    
    def print_summary(self) -> None:
        """Print a summary of sync status"""
        if not self.sync_status:
            logger.info("No models were verified.")
            return
        
        total_models = len(self.sync_status)
        synced_models = len([s for s in self.sync_status.values() if s['is_synced']])
        models_with_missing = len([s for s in self.sync_status.values() if s['missing_in_rba'] > 0])
        models_with_extra = len([s for s in self.sync_status.values() if s['extra_in_rba'] > 0])
        
        total_missing = sum(s['missing_in_rba'] for s in self.sync_status.values())
        total_extra = sum(s['extra_in_rba'] for s in self.sync_status.values())
        
        logger.info("\n" + "="*100)
        logger.info("SYNC VERIFICATION SUMMARY")
        logger.info("="*100)
        
        logger.info(f"{'Model':<40} {'OS Hub':<10} {'RBA':<10} {'Missing':<10} {'Extra':<10} {'Status':<10}")
        logger.info("-" * 100)
        
        for model_key, status in sorted(self.sync_status.items()):
            status_icon = "✓" if status['is_synced'] else "✗"
            logger.info(f"{model_key:<40} {status['os_count']:<10} {status['rba_count']:<10} {status['missing_in_rba']:<10} {status['extra_in_rba']:<10} {status_icon:<10}")
        
        logger.info("-" * 100)
        logger.info(f"{'TOTALS':<40} {sum(s['os_count'] for s in self.sync_status.values()):<10} {sum(s['rba_count'] for s in self.sync_status.values()):<10} {total_missing:<10} {total_extra:<10}")
        
        logger.info("\nSUMMARY:")
        logger.info(f"  • Total models: {total_models}")
        logger.info(f"  • Fully synced models: {synced_models}")
        logger.info(f"  • Models with missing records: {models_with_missing}")
        logger.info(f"  • Models with extra records: {models_with_extra}")
        logger.info(f"  • Total missing records: {total_missing}")
        logger.info(f"  • Total extra records: {total_extra}")
        
        if models_with_missing > 0:
            logger.info("\nMODELS WITH MISSING RECORDS:")
            for model_key, status in sorted(self.sync_status.items()):
                if status['missing_in_rba'] > 0:
                    logger.info(f"  • {model_key}: {status['missing_in_rba']} missing records")
        
        logger.info("="*100)


class Command(BaseCommand):
    help = "Verify sync status between OS Hub and RBA databases"

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            required=False,
            help='Specific model to verify (app_label.ModelName)'
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed missing UUIDs (first 50)'
        )
        parser.add_argument(
            '--missing-only',
            action='store_true',
            help='Only show models with missing records'
        )

    def handle(self, *args, **options):
        verifier = SyncVerifier()
        
        if options['model']:
            # Verify specific model
            try:
                app_label, model_name = options['model'].split('.')
                model = apps.get_model(app_label, model_name)
                
                if model not in verifier.models_with_uuid:
                    self.stdout.write(
                        self.style.ERROR(f"Model {options['model']} does not have a UUID field or does not exist in both databases.")
                    )
                    return
                
                status = verifier.verify_model_sync(model)
                verifier.sync_status[status['model_key']] = status
                
                if options['detailed'] and status['missing_in_rba'] > 0:
                    missing_uuids = verifier.get_missing_uuids_detailed(model)
                    logger.info(f"\nDetailed missing UUIDs for {status['model_key']}:")
                    for uuid in missing_uuids:
                        logger.info(f"  {uuid}")
                
            except (ValueError, LookupError) as e:
                self.stdout.write(
                    self.style.ERROR(f"Invalid model format or model not found: {e}")
                )
                return
        else:
            # Verify all models
            verifier.verify_all_models()
            
            if options['detailed']:
                logger.info("\n" + "="*100)
                logger.info("DETAILED MISSING UUIDS")
                logger.info("="*100)
                
                for model_key, status in sorted(verifier.sync_status.items()):
                    if status['missing_in_rba'] > 0:
                        try:
                            app_label, model_name = model_key.split('.')
                            model = apps.get_model(app_label, model_name)
                            missing_uuids = verifier.get_missing_uuids_detailed(model)
                            
                            logger.info(f"\n{model_key} - Missing UUIDs (showing first 50):")
                            for uuid in missing_uuids:
                                logger.info(f"  {uuid}")
                            
                            if status['missing_in_rba'] > 50:
                                logger.info(f"  ... and {status['missing_in_rba'] - 50} more")
                        except Exception as e:
                            logger.error(f"Error getting detailed UUIDs for {model_key}: {e}")
        
        # Print summary
        if not options['missing_only']:
            verifier.print_summary()
        else:
            # Only show models with missing records
            models_with_missing = {k: v for k, v in verifier.sync_status.items() if v['missing_in_rba'] > 0}
            if models_with_missing:
                logger.info("\n" + "="*100)
                logger.info("MODELS WITH MISSING RECORDS")
                logger.info("="*100)
                
                logger.info(f"{'Model':<40} {'OS Hub':<10} {'RBA':<10} {'Missing':<10}")
                logger.info("-" * 80)
                
                for model_key, status in sorted(models_with_missing.items()):
                    logger.info(f"{model_key:<40} {status['os_count']:<10} {status['rba_count']:<10} {status['missing_in_rba']:<10}")
                
                logger.info("-" * 80)
                total_missing = sum(s['missing_in_rba'] for s in models_with_missing.values())
                logger.info(f"{'TOTALS':<40} {sum(s['os_count'] for s in models_with_missing.values()):<10} {sum(s['rba_count'] for s in models_with_missing.values()):<10} {total_missing:<10}")
            else:
                logger.info("✓ All models are fully synced!") 