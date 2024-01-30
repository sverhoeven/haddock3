"""Compute contacts and generate heatmaps."""
from copy import deepcopy
from pathlib import Path

from haddock.core.typing import Any, FilePath, SupportsRunT
from haddock.libs.libparallel import Scheduler
from haddock.modules import BaseHaddockModule
from haddock.modules.analysis.contactmap.contmap import (
    ContactsMap,
    ContactsMapJob,
    ClusteredContactMap,
    get_clusters_sets,
    make_contactmap_report,
    topX_models,
    )


RECIPE_PATH = Path(__file__).resolve().parent
DEFAULT_CONFIG = Path(RECIPE_PATH, "defaults.yaml")


class HaddockModule(BaseHaddockModule):
    """HADDOCK3 module to compute complexes contacts and generate heatmap."""

    name = RECIPE_PATH.name

    def __init__(
            self,
            order: int,
            path: Path,
            *ignore: Any,
            init_params: FilePath = DEFAULT_CONFIG,
            **everything: Any,
            ) -> None:
        """Initialize class."""
        super().__init__(order, path, init_params)

    @classmethod
    def confirm_installation(cls) -> None:
        """Confirm if contact executable is compiled."""
        return

    def _run(self) -> None:
        """Execute module."""
        # Get the models generated in previous step
        if type(self.previous_io) == iter:
            _e = "This module cannot come after one that produced an iterable."
            self.finish_with_error(_e)
        try:
            models = self.previous_io.retrieve_models(individualize=True)
        except AttributeError as e:
            self.finish_with_error(e)

        # Initiate holder of all jobs to be run by the `Scheduler`
        contact_jobs: list[SupportsRunT] = []
        # Obtain clusters
        clusters_sets = get_clusters_sets(models)
        # Loop over clusters
        for clustid, clt_models in clusters_sets.items():
            # In case of unclustered models
            if clustid is None:
                # Obtain subset of top models
                top_models = topX_models(clt_models, topX=self.params["topX"])

                # Create single model analysis params
                single_models_params = deepcopy(self.params)
                single_models_params["single_model_analysis"] = True

                # Loop over models to analyse
                for model in top_models:
                    modelfname = Path(model.file_name).stem
                    # Create a job object
                    contmap_job = ContactsMapJob(
                        Path(f"Unclustered_contmap_{modelfname}"),
                        single_models_params,
                        modelfname,
                        # Create a contact map object
                        ContactsMap(
                            Path(model.rel_path),
                            Path(f"Unclustered_contmap_{modelfname}"),
                            modelfname,
                            single_models_params,
                            ),
                        )
                    contact_jobs.append(contmap_job)

            # For clustered models
            else:
                # Create a job object
                contmap_job = ContactsMapJob(
                    Path(f"cluster{clustid}_contmap"),
                    self.params,
                    f"Cluster_{clustid}",
                    # Create a contact map object
                    ClusteredContactMap(
                        [Path(model.rel_path) for model in clt_models],
                        Path(f"cluster{clustid}_contmap"),
                        self.params,
                        ),
                    )
                contact_jobs.append(contmap_job)

        # Initiate `Scheduler`
        scheduled = Scheduler(contact_jobs, ncores=self.params['ncores'])
        # Run all jobs
        scheduled.run()

        # Generate report
        make_contactmap_report(contact_jobs, "ContactMapReport.html")

        # Send models to the next step, no operation is done on them
        self.output_models = models
        self.export_io_models()
