package me.constfold.speculum

import com.jpexs.decompiler.flash.SWF
import com.jpexs.decompiler.flash.abc.ABC
import com.jpexs.decompiler.flash.abc.ScriptPack
import com.jpexs.decompiler.flash.abc.types.Multiname
import com.jpexs.decompiler.flash.abc.types.Namespace
import com.jpexs.decompiler.flash.gfx.GfxConvertor
import com.jpexs.decompiler.flash.tags.DefineBinaryDataTag
import com.jpexs.decompiler.flash.tags.DefineSpriteTag
import com.jpexs.decompiler.flash.tags.FrameLabelTag
import com.jpexs.decompiler.flash.tags.Tag
import java.io.File
import kotlin.system.exitProcess

class Main {
    companion object {
        @JvmStatic
        fun main(args: Array<String>) {
            if (args.size < 2) {
                println("Usage: program <command>")
                exitProcess(-1)
            }
            try {
                runCommand(args)
            } catch (e: Exception) {
                println("Error: ${e.message}")
                exitProcess(-1)
            }
        }

        private fun runCommand(args: Array<String>) {
            when (args[0]) {
                "merge" -> {
                    if (args.size != 4) {
                        println("Usage: program merge <original> <new> <output>")
                        exitProcess(-1)
                    }
                    File(args[1]).inputStream().use { originalStream ->
                        val original = SWF(originalStream, false)
                        File(args[2]).inputStream().use { newStream ->
                            val new = SWF(newStream, false)
                            merge(original, new)
                            save(original, File(args[3]))
                        }
                    }
                }

                "inject" -> {
                    if (args.size != 4) {
                        println("Usage: program inject <swf> <namespace> <output>")
                        exitProcess(-1)
                    }
                    File(args[1]).inputStream().use { originalStream ->
                        val swf = SWF(originalStream, false)
                        inject(swf, getHelperClass(swf, args[2]))
                        save(swf, File(args[3]))
                    }
                }

                "info" -> {
                    if (args.size != 2) {
                        println("Usage: program info <file>")
                        exitProcess(-1)
                    }
                    File(args[1]).inputStream().use { stream ->
                        val swf = SWF(stream, false)
                        val json = "{" +
                                "\"version\" : ${swf.version}," +
                                "\"frame_rate\" : ${swf.frameRate}," +
                                "\"isAS3\" : ${swf.isAS3}," +
                                "\"width\" : ${swf.displayRect.width}," +
                                "\"height\" : ${swf.displayRect.height}" +
                                "}"
                        println(json)
                    }
                }

                "extract" -> {
                    if (args.size != 3) {
                        println("Usage: program extract <swf> <output>")
                        exitProcess(-1)
                    }
                    File(args[1]).inputStream().use { stream ->
                        val swf = SWF(stream, false)

                        save(extract(swf), File(args[2]))
                    }
                }

                else -> {
                    println("Unknown command ${args[0]}")
                    exitProcess(-1)
                }
            }
        }

        @JvmStatic
        fun merge(original: SWF, new: SWF) {
            val al = original.abcList
            val firstAbc = al[0]

            original.debuggerPackage = "speculum"

            for (ds in new.abcList) {
                (ds as Tag).swf = original
                original.addTagBefore(ds, firstAbc as Tag)
                original.abcList.add(original.abcList.indexOf(firstAbc), ds)
                (ds as Tag).isModified = true

                val ft = original.fileAttributes
                ft.useNetwork = true
                ft.isModified = true
            }
        }

        @JvmStatic
        fun save(swf: SWF, file: File) {
            var swfToSave = swf
            if (swfToSave.gfx) {
                swfToSave = GfxConvertor().convertSwf(swf)
            }
            swfToSave.saveTo(file.outputStream())
        }

        @JvmStatic
        fun getHelperClass(swf: SWF, namespace: String): List<ScriptPack> {
            val allAbcList: MutableList<ABC> = ArrayList()
            for (ac in swf.abcList) {
                allAbcList.add(ac.abc)
            }
            val list = ArrayList<ScriptPack>()
            for (ac in swf.abcList) {
                val a = ac.abc
                for (m in a.getScriptPacks(namespace, allAbcList)) {
                    if (m.classPath.packageStr.toRawString() == namespace) {
                        list.add(m)
                    }
                }
            }

            check(list.size != 0) { "Can not resolve $namespace" }
            return list
        }

        @JvmStatic
        fun inject(swf: SWF, pkg: List<ScriptPack>) {
            val packageName = pkg[0].classPath.packageStr.toRawString()
            for (ct in swf.abcList) {
                val a = ct.abc
                if (pkg.find { it.abc == a } != null) {
                    continue
                }
                val packageNs = a.constants.getNamespaceId(Namespace.KIND_PACKAGE, packageName, 0, true)
                for (i in 0 until a.constants.multinameCount) {
                    val m = a.constants.getMultiname(i) ?: continue
                    var rawNsName = m.getNameWithNamespace(a.constants, true).toRawString()
                    if (m.kind == Multiname.MULTINAME) {
                        val simpleName = m.getName(a.constants, ArrayList(), true, false)

                        val nsToSearch = when (simpleName) {
                            "URLLoader" -> "flash.net"
                            "Loader" -> "flash.display"
                            "ExternalInterface" -> "flash.external"
                            else -> continue
                        }

                        for (ns in a.constants.getNamespaceSet(m.namespace_set_index).namespaces) {
                            if (a.constants.namespaceToString(ns) == nsToSearch) {
                                m.kind = Multiname.QNAME
                                m.namespace_index = ns
                                m.namespace_set_index = 0
                                rawNsName = m.getNameWithNamespace(a.constants, true).toRawString()
                                break
                            }
                        }
                    }
                    when (rawNsName) {
                        "flash.net.URLLoader" -> {
                            m.namespace_index = packageNs
                            m.name_index = a.constants.getStringId("SpeculumInterceptorURLLoader", true)
                            (ct as Tag).isModified = true
                        }

                        "flash.display.Loader" -> {
                            m.namespace_index = packageNs
                            m.name_index = a.constants.getStringId("SpeculumInterceptorLoader", true)
                            (ct as Tag).isModified = true
                        }

                        "flash.external.ExternalInterface" -> {
                            m.namespace_index = packageNs
                            m.name_index = a.constants.getStringId("SpeculumInterceptorExternalInterface", true)
                            (ct as Tag).isModified = true
                        }
                    }
                }
            }
        }

        @JvmStatic
        fun extract(swf: SWF): SWF {
            val frames = swf.timeline.frames
            assert(frames.size == 2) { "Expected 2 frames, got ${frames.size}" }

            for (frame in frames) {
                assert(frame.innerTags.size == 1) { "Expected 1 tag, got ${frame.innerTags.size}" }
                val tag = frame.innerTags[0] as? FrameLabelTag
                    ?: throw Exception("Expected FrameLabelTag, got ${frame.innerTags[0].javaClass}")
                assert(tag.name == "prefor_System4399Manager" || tag.name == "L4399Main") {
                    "Expected FrameLabelTag with name System4399Manager or L4399Main, got ${tag.name}"
                }
                if (tag.name != "L4399Main") continue
                val dbdTags = frame.allInnerTags.filterIsInstance<DefineBinaryDataTag>()
                assert(dbdTags.size == 1) { "Expected 1 DefineBinaryDataTag, got ${dbdTags.size}" }

                dbdTags[0].loadEmbeddedSwf()
                return dbdTags[0].innerSwf!!
            }
            throw Exception("No DefineBinaryDataTag found")
        }
    }
}

private fun SWF.addTagBefore(newTag: Tag, targetTag: Tag) {
    val tim = targetTag.timelined
    val index = tim.indexOfTag(targetTag)
    if (index < 0) {
        return
    }
    tim.addTag(index, newTag)
    tim.resetTimeline()
    if (tim is DefineSpriteTag) {
        tim.frameCount = tim.getTimeline().frameCount
    } else if (tim is SWF) {
        tim.frameCount = tim.getTimeline().frameCount
    }
    newTag.timelined = tim
}
