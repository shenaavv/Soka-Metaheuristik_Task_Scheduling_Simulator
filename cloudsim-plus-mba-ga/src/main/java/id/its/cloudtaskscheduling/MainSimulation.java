package id.its.cloudtaskscheduling;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

/**
 * Runs both schedulers from one combined entry point.
 *
 * <p>The original algorithms use incompatible CloudSim Plus major versions,
 * so each one is launched in its own Maven process to keep the classpaths
 * isolated.</p>
 */
public final class MainSimulation {
    private MainSimulation() {
    }

    public static void main(String[] args) {
        System.out.println("=================================================");
        System.out.println(" COMBINED GA + MBA CLOUD TASK SCHEDULING");
        System.out.println("=================================================");
        runScheduler("GENETIC ALGORITHM", Path.of("../cloudsim-plus-ga"));
        runScheduler("MODIFIED BAT ALGORITHM", Path.of("../cloudsim-plus-mba"));
        saveCombinedResults();
    }

    private static void runScheduler(String label, Path projectDirectory) {
        System.out.printf("%n--- %s ---%n%n", label);
        try {
            Process process = new ProcessBuilder(
                    "mvn", "-q", "compile", "exec:java")
                    .directory(projectDirectory.toFile())
                    .inheritIO()
                    .start();
            int exitCode = process.waitFor();
            if (exitCode != 0) {
                throw new IllegalStateException(
                        label + " exited with code " + exitCode);
            }
        } catch (IOException e) {
            throw new IllegalStateException(
                    "Could not start " + label + " from " + projectDirectory, e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException(label + " was interrupted", e);
        }
    }

    private static void saveCombinedResults() {
        Path combinedResults = Path.of("results");
        try {
            Files.createDirectories(combinedResults);
            copyIfExists(
                    Path.of("../cloudsim-plus-ga/results/metrics.txt"),
                    combinedResults.resolve("ga_metrics.txt"));
            copyIfExists(
                    Path.of("../cloudsim-plus-ga/results/ga_mapping.csv"),
                    combinedResults.resolve("ga_mapping.csv"));
            copyIfExists(
                    Path.of("../cloudsim-plus-mba/results/metrics.txt"),
                    combinedResults.resolve("mba_metrics.txt"));
            copyIfExists(
                    Path.of("../cloudsim-plus-mba/results/mba_mapping.csv"),
                    combinedResults.resolve("mba_mapping.csv"));
            System.out.printf("%n[INFO] Combined results saved to %s%n",
                    combinedResults.toAbsolutePath());
        } catch (IOException e) {
            throw new IllegalStateException(
                    "Could not save combined GA/MBA results", e);
        }
    }

    private static void copyIfExists(Path source, Path destination)
            throws IOException {
        if (Files.isRegularFile(source)) {
            Files.copy(source, destination, StandardCopyOption.REPLACE_EXISTING);
        }
    }
}
