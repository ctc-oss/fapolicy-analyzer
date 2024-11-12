use human_panic::{setup_panic, Metadata};

pub fn setup_human_panic() {
    setup_panic!(
        Metadata::new(env!("CARGO_PKG_NAME"), env!("CARGO_PKG_VERSION"))
            .authors("CTC-OSS and contributors")
            .homepage("https://github.com/ctc-oss/fapolicy-analyzer")
            .support(
                [
                    "- Open a GitHub issue on the fapolicy-analyzer project page",
                    "- Open a Red Hat Bugzilla issue for the fapolicy-analyzer package"
                ]
                .join("\n")
            )
    );
}
